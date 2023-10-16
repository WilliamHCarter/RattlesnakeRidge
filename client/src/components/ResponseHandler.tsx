import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";
import { TextStyles } from "./Typewriter";
import {
  SelectOptionCommand,
  castCommand,
  extractTextContent,
  extractTextStyles,
} from "../Command";

function InputHandler() {
  const [conversation, setConversation] = useState<string[]>([]);
  const [gameID, setGameID] = useState<string | undefined>("");
  const [_styles, setStyles] = useState<TextStyles>();
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);
  const [gameOver, setGameOver] = useState<boolean>(false);

 useEffect(() => {
  let isMounted = true;
  const fetchData = async () => {
    const response = await fetch("http://127.0.0.1:5000/start");
    if (!response.ok || !isMounted) {
      return;
    }

    const data = await response.json();
    if (data.message && typeof data.message === "string") {
      setConversation((prev) => [...prev, data.message]);
      setGameID(data.game_id);
    }
  };
  fetchData();

  return () => {
    isMounted = false; 
  };
}, []);

  const sendRequest = async (userInput: string) => {
    const response = await fetch("http://127.0.0.1:5000/play/" + gameID, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: userInput }),
    });
    if (response.ok) {
      const data = await response.json();
      console.log(data);
      return data;
    }
    return Error("Error: Server Request Failed.");
  };

  const handleUserInput = async (userInput: string) => {
    if (gameOver) return;
    if (lastMessage?.type == "SelectOptionCommand" && userInput !== "") {
      let last: SelectOptionCommand = lastMessage as SelectOptionCommand;
      if (!last.options.some((tuple) => tuple.includes(userInput))) {
        let error = "Invalid option. Please try again.";
        setConversation((prev) => [...prev, error]);
        return;
      }
    }

    let data = await sendRequest(userInput);
    let response = castCommand(data.response);
    let styles: TextStyles = extractTextStyles(response);
    let text: string[] = extractTextContent(response);
    if (response.is_game_over) {
      setGameOver(true);
    }

    let uText = userInput ? "\nYou: " + userInput : "";
    setConversation((prev) => [...prev, uText, ...text]);

    setStyles(styles);
    setLastMessage(
      response.type == "SelectOptionCommand"
        ? (response as SelectOptionCommand)
        : undefined
    );
    if (!response.expects_user_input && !response.is_game_over) handleUserInput("");
  };

  return (
    <div className="mx-auto flex flex-col">
      <CrtScreen conversation={conversation} />
      <InputField onSend={handleUserInput} />
    </div>
  );
}

export default InputHandler;
