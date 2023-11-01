import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { SelectOptionCommand } from "../Command";
import { startGame, ply, validateOption } from "../API";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]);
  const [styleArray, setStyleArray] = useState<TextStyles[]>([
    new TextStyles("init"),
  ]);
  const [gameID, setGameID] = useState<string>("");
  const [isTyping, setIsTyping] = useState(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [restartGame, setRestartGame] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);

  const handleConversation = (message: string[], style: TextStyles[]) => {
    setConversation(prev => [...prev, ...message]);
    let isGameStarted = styleArray[0].message === "init";
    setStyleArray(isGameStarted ? style : prev => [...prev, ...style]);
  };
  

  const handleTypeState = (typing: boolean) => {
    if (typing != isTyping) {
      setIsTyping(typing);
    }
  };

  const restart = async () => {
    setRestartGame(true);
    setConversation([]);
    setGameOver(false);
  };

  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;
    startGame({ handleConversation, setGameID, isMounted });
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

  const handleUserInput = async (userInput: string) => {
    if (gameOver) return;
    if (validateOption(lastMessage, userInput, handleConversation)) return;

    let data = await ply(gameID, userInput, gameOver, handleConversation);

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
        style={styleArray}
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
