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
  const [styles, setStyles] = useState<TextStyles>(new TextStyles());
  const [lastMessage, setLastMessage] = useState<
    SelectOptionCommand | undefined
  >(undefined);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleTypeState = (typing: boolean) => {
    setIsTyping(typing);
  };

  // Fetch the initial message from the server when the component mounts.
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://127.0.0.1:5000/start");
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        if (typeof data.message === "string" && data.message !== undefined) {
          setConversation((prev: string[]) => [
            ...prev,
            data.message as string,
          ]);
        }
        setGameID(() => data.game_id);
      } else {
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (gameID) {
      handleUserInput("");
    }
  }, [gameID]);

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
    if (!response.expects_user_input && !response.is_game_over)
      handleUserInput("");
  };

  return (
    <div className="mx-auto flex flex-col">
      <CrtScreen conversation={conversation} style={styles} onTypeState={handleTypeState} />
      <InputField onSend={handleUserInput} disabled={isTyping} gameOver={gameOver}/>
    </div>
  );
}

export default InputHandler;
