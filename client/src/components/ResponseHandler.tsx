import { useEffect, useState, useRef } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { SelectOptionCommand, StreamingMessageCommand } from "../Command";
import { startGame, ply, validateOption, loadGame, endGame, streamResponse } from "../API";
import { RequestQueue } from "../RequestQueue";

function ResponseHandler({
  setFullscreen,
}: {
  setFullscreen: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [conversation, setConversation] = useState<string[]>([]);
  const [styleArray, setStyleArray] = useState<TextStyles[]>([]);
  const [gameID, setGameID] = useState<string>("");
  const [isTyping, setIsTyping] = useState(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [newGame, setNewGame] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);

  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingText, setCurrentStreamingText] = useState("");
  const [currentStreamingAgent, setCurrentStreamingAgent] = useState("");

  // Request queue to prevent concurrent backend calls
  const requestQueue = useRef(new RequestQueue());

  const handleConversation = (message: string[], style: TextStyles[]) => {
    setConversation((prev) => [...prev, ...message]);
    setStyleArray((prev) => [...prev, ...style]);
  };

  const handleTypeState = (typing: boolean) => {
    setIsTyping(typing);
  };

  const handleStreaming = async (streamingCmd: StreamingMessageCommand) => {
    console.log(`handleStreaming: starting for ${streamingCmd.agent_name}, stream_id=${streamingCmd.stream_id}`);
    console.log(`handleStreaming: expects_user_input=${streamingCmd.expects_user_input}, is_game_over=${streamingCmd.is_game_over}`);

    setIsStreaming(true);
    setCurrentStreamingAgent(streamingCmd.agent_name);
    setCurrentStreamingText("");

    // Add the initial "Agent: " part to conversation
    const initialMessage = `${streamingCmd.agent_name}: `;
    console.log(`handleStreaming: adding initial message to conversation: '${initialMessage}'`);
    handleConversation([initialMessage], [new TextStyles(initialMessage, false, 0)]);

    try {
      console.log(`handleStreaming: calling streamResponse...`);
      await streamResponse(
        streamingCmd.stream_id,
        streamingCmd.agent_name,
        // onChunk: called for each token
        (chunk: string) => {
          console.log(`handleStreaming: received chunk: '${chunk}'`);

          // Update the last message in conversation with accumulated text
          setConversation((prev) => {
            const newConv = [...prev];
            const currentMessage = newConv[newConv.length - 1];
            // Add the chunk to the existing message (which already has the prefix)
            newConv[newConv.length - 1] = currentMessage + chunk;
            console.log(`handleStreaming: conversation updated, last message now: '${newConv[newConv.length - 1]}'`);
            return newConv;
          });

          setCurrentStreamingText((prev) => {
            const newText = prev + chunk;
            console.log(`handleStreaming: currentStreamingText updated to: '${newText}'`);
            return newText;
          });
        },
        // onComplete: called when streaming is done
        (fullText: string) => {
          console.log(`handleStreaming: streaming completed, full text: '${fullText}'`);
          setIsStreaming(false);
          setCurrentStreamingText("");

          // No need to update conversation - it was updated during each chunk
          // The conversation should already have the complete text by now
          console.log(`handleStreaming: streaming completed - conversation already has complete text`);

          // Auto-continue with empty input if this command expects input
          if (streamingCmd.expects_user_input && !streamingCmd.is_game_over) {
            console.log(`handleStreaming: auto-continuing with empty input`);
            handleUserInput("");
          } else {
            console.log(`handleStreaming: not auto-continuing (expects_user_input=${streamingCmd.expects_user_input}, is_game_over=${streamingCmd.is_game_over})`);
          }
        },
        // onError: called if streaming fails
        (error: string) => {
          console.error(`handleStreaming: streaming error: ${error}`);
          setIsStreaming(false);
          setCurrentStreamingText("");
          const errorMessage = `Streaming error: ${error}`;
          handleConversation([errorMessage], [new TextStyles(errorMessage, false, 0)]);
          console.error("Streaming error:", error);
        }
      );
      console.log(`handleStreaming: streamResponse completed successfully`);
    } catch (error) {
      console.error(`handleStreaming: failed to start streaming:`, error);
      setIsStreaming(false);
      setCurrentStreamingText("");
    }
  };

  const restart = () => {
    localStorage.removeItem("game_id");
    setGameID("");
    setConversation([]);
    setStyleArray([]);
    setGameOver(false);
    setLastMessage(undefined);
    startGameAndHandleInput();
  };

  const startGameAndHandleInput = async () => {
    await startGame({ handleConversation, setGameID, handleUserInput });
    handleUserInput("");
    setNewGame(false);
  };

  useEffect(() => {
    setGameID(localStorage.getItem("game_id") || "");
  }, []);

  useEffect(() => {
    const loadSavedGame = async () => {
      if (gameID && conversation.length === 0) {
        try {
          await loadGame({ handleConversation, setGameID, handleUserInput });
          setNewGame(false);
        } catch (error) {
          console.error("Error loading game:", error);
          return;
        }
      }
    };
    loadSavedGame();
  }, [gameID, conversation.length]);

  const handleUserInput = async (userInput: string) => {
    console.log(`handleUserInput: called with input: '${userInput}'`);
    console.log(`handleUserInput: isTyping=${isTyping}, isStreaming=${isStreaming}`);

    // Validate input first (doesn't need to be queued)
    if (validateOption(lastMessage, userInput, handleConversation)) {
      console.log(`handleUserInput: input validation returned early`);
      return;
    }

    // Queue the request to prevent concurrent backend calls
    await requestQueue.current.enqueue(async () => {
      console.log(`handleUserInput: processing queued request for input: '${userInput}'`);
      const data = await ply(userInput, handleConversation);
      const cmd = data?.command;

      console.log(`handleUserInput: received command type: ${cmd?.type}`);
      console.log(`handleUserInput: command properties:`, {
        expects_user_input: cmd?.expects_user_input,
        is_game_over: cmd?.is_game_over
      });

      setLastMessage(
        cmd?.type == "SelectOptionCommand"
          ? (cmd as SelectOptionCommand)
          : undefined,
      );

      if (cmd?.is_game_over) {
        console.log(`handleUserInput: game over detected`);
        setGameOver(true);
        endGame();
        return;
      }

      // Handle streaming commands
      if (cmd?.type == "StreamingMessageCommand") {
        console.log(`handleUserInput: processing StreamingMessageCommand`);
        const streamingCmd = cmd as StreamingMessageCommand;
        await handleStreaming(streamingCmd);
        return;
      }

      // Auto-send for commands that don't expect user input
      // This will be queued after the current request completes
      if (cmd && !cmd.expects_user_input && !cmd.is_game_over) {
        console.log(`handleUserInput: auto-continuing with empty input (cmd expects no user input)`);
        handleUserInput("");
      } else {
        console.log(`handleUserInput: not auto-continuing (expects_user_input=${cmd?.expects_user_input}, is_game_over=${cmd?.is_game_over})`);
      }
    });
  };

  return (
    <div className="mx-auto flex flex-col">
      <CrtScreen
        conversation={conversation}
        style={styleArray}
        onTypeState={handleTypeState}
        isFullscreen={isFullscreen}
        toggleFullscreen={() => {
          setIsFullscreen(!isFullscreen);
          setFullscreen(!isFullscreen);
        }}
      />
      <InputField
        onSend={handleUserInput}
        newGame={newGame}
        disabled={isTyping || isStreaming}
        gameOver={gameOver}
        onRestart={restart}
        isFullscreen={isFullscreen}
      />
    </div>
  );
}

export default ResponseHandler;
