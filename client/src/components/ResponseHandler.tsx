import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { SelectOptionCommand } from "../Command";
import { startGame, playGame } from "../API";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]);
  const [gameID, setGameID] = useState<string>("");
  const [styles, setStyles] = useState<TextStyles>(new TextStyles());
  const [isTyping, setIsTyping] = useState(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [restartGame, setRestartGame] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);

  const handleTypeState = (typing: boolean) => {
    setIsTyping(typing);
  };

  const restart = async () => {
    setRestartGame(true);
    setConversation([]);
    setGameOver(false);
  };

  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;
    startGame({ setConversation, setGameID, setStyles, isMounted });

    return () => {
      mounted = false;
      setRestartGame(false);
    };
  }, [restartGame]);

  useEffect(() => {
    if (gameID) {
      handleUserInput("");
    }
  }, [gameID]);

  const validateOption = (lastMessage: any, userInput: string): boolean => {
    if (lastMessage?.type == "SelectOptionCommand" && userInput !== "") {
      let last: SelectOptionCommand = lastMessage as SelectOptionCommand;
      if (!last.options.some((tuple) => tuple.includes(userInput))) {
        let error = "Invalid option. Please try again.";
        setConversation((prev) => [...prev, error]);
        return true;
      }
    }
    return false;
  };

  const handleUserInput = async (userInput: string) => {
    if (gameOver) return;
    if (validateOption(lastMessage, userInput)) return;

    let data = await playGame(gameID, userInput, gameOver, setConversation);
    if (data?.styles) {
      setStyles(data?.styles);
    }
    setLastMessage(
      data?.command.type == "SelectOptionCommand"
        ? (data.command as SelectOptionCommand)
        : undefined
    );
    if (!data?.command.expects_user_input && !data?.command.is_game_over)
      handleUserInput("");
  };

  return (
    <div className="mx-auto flex flex-col">
      <CrtScreen
        conversation={conversation}
        style={styles}
        onTypeState={handleTypeState}
      />
      <InputField
        onSend={handleUserInput}
        disabled={isTyping}
        gameOver={gameOver}
        onRestart={restart}
      />
    </div>
  );
}

export default ResponseHandler;
