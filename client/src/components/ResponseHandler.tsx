import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { GenericMessageCommand, SelectOptionCommand } from "../Command";
import { startGame, ply, validateOption, loadGame, endGame } from "../API";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]);
  const [styleArray, setStyleArray] = useState<TextStyles[]>([]);
  const [gameID, setGameID] = useState<string>("");
  const [isTyping, setIsTyping] = useState(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [newGame, setNewGame] = useState(true);
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);

  const handleConversation = (message: string[], style: TextStyles[]) => {
    setConversation((prev) => [...prev, ...message]);
    setStyleArray((prev) => [...prev, ...style]);
  };

  const handleTypeState = (typing: boolean) => {
    if (typing != isTyping) {
      setIsTyping(typing);
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
    console.log("hewwo");
    var game_id = localStorage.getItem("game_id");
    if (game_id) {
      setGameID(game_id);
    }
  }, []);

  useEffect(() => {
    console.log("uwu");
    if (gameID && conversation.length === 0) {
      console.log("hmm");
      var rsp = loadGame({ handleConversation, setGameID, handleUserInput });
      if (!rsp){
        console.log("hmm2")
        return;
      }
      setNewGame(false);
    }
  }, [gameID]);

  const handleUserInput = async (userInput: string) => {
    if (validateOption(lastMessage, userInput, handleConversation)) return;

    let id = localStorage.getItem("game_id") as string;
    let data = await ply(id, userInput, handleConversation);
    setLastMessage(
      data?.command.type == "SelectOptionCommand"
        ? (data.command as SelectOptionCommand)
        : undefined
    );
    if (
      data &&
      !data?.command.expects_user_input &&
      !data?.command.is_game_over
    ) {
      handleUserInput("");
    }
    var msg = data?.command as GenericMessageCommand;
    if (
      data?.command.is_game_over ||
      msg?.message.includes("the game is over")
    ) {
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
      />
      <InputField
        onSend={handleUserInput}
        newGame={newGame}
        disabled={isTyping}
        gameOver={gameOver}
        onRestart={restart}
      />
    </div>
  );
}

export default ResponseHandler;
