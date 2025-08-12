import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { SelectOptionCommand } from "../Command";
import { startGame, ply, validateOption, loadGame, endGame } from "../API";

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

  const handleConversation = (message: string[], style: TextStyles[]) => {
    setConversation((prev) => [...prev, ...message]);
    setStyleArray((prev) => [...prev, ...style]);
  };

  const handleTypeState = (typing: boolean) => {
    setIsTyping(typing);
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
    if (validateOption(lastMessage, userInput, handleConversation)) return;
    const data = await ply(userInput, handleConversation);
    const cmd = data?.command;
    setLastMessage(
      cmd?.type == "SelectOptionCommand"
        ? (cmd as SelectOptionCommand)
        : undefined,
    );
    if (cmd && !cmd.expects_user_input && !cmd.is_game_over) {
      handleUserInput("");
    }

    if (cmd?.is_game_over) {
      setGameOver(true);
      endGame();
    }
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
        disabled={isTyping}
        gameOver={gameOver}
        onRestart={restart}
        isFullscreen={isFullscreen}
      />
    </div>
  );
}

export default ResponseHandler;
