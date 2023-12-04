import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import { GenericMessageCommand, SelectOptionCommand } from "../Command";
import { startGame, ply, validateOption, loadGame } from "../API";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]);
  const [styleArray, setStyleArray] = useState<TextStyles[]>([
    new TextStyles("init"),
  ]);
  const [gameID, setGameID] = useState<string>("");
  const [isTyping, setIsTyping] = useState(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [gameStarted, setGameStarted] = useState(false);
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

  const restart = async () => {
    setGameID("");
    setConversation([]);
    setStyleArray([new TextStyles("init")]);
    setGameOver(false);
    setLastMessage(undefined);
    localStorage.removeItem("game_id");
    setGameStarted(true);
    startGameAndHandleInput("");
  };

  const startGameAndHandleInput = async (game_id: string) => {
    if (gameStarted && !game_id) {
      await startGame({ handleConversation, setGameID, handleUserInput });
      handleUserInput("");
      setGameStarted(true);
    }
  };

  useEffect(() => {
    startGameAndHandleInput(gameID);
  }, [gameStarted]);

  //Check Local Storage for game_id
  useEffect(() => {
    var game_id = localStorage.getItem("game_id");
    if (game_id) {
      setGameID(game_id);
    }
    if (!game_id) {
      setGameStarted(true);
    }
  }, []);

  useEffect(() => {
    if (gameID && conversation.length === 0) {
      loadGame({ handleConversation, setGameID, handleUserInput });
    }
  }, [gameID]);

  const handleUserInput = async (userInput: string) => {
    if (gameOver) return;

    if (validateOption(lastMessage, userInput, handleConversation)) return;

    let id = localStorage.getItem("game_id") as string;
    let data = await ply(id, userInput, gameOver, handleConversation);

    setLastMessage(
      data?.command.type == "SelectOptionCommand"
        ? (data.command as SelectOptionCommand)
        : undefined
    );
    if (!data?.command.expects_user_input && !data?.command.is_game_over) {
      handleUserInput("");
    }
    var msg = data?.command as GenericMessageCommand;
    if (
      data?.command.is_game_over ||
      msg?.message.includes("the game is over")
    ) {
      setGameOver(true);
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
