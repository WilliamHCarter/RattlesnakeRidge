import { Dispatch, SetStateAction } from "react";
import {
  SelectOptionCommand,
  castCommand,
  extractTextContent,
  extractTextStyles,
} from "./Command";
import { TextStyles } from "./components/Typewriter";

interface SGProps {
  handleConversation: Function;
  setGameID: Dispatch<SetStateAction<string>>;
  isMounted: () => boolean;
}

export const startGame = async ({
  handleConversation,
  setGameID,
  isMounted,
}: SGProps) => {
  const response = await fetch("http://127.0.0.1:5000/start");

  if (!response.ok || !isMounted()) {
    return;
  }

  const data = await response.json();
  console.debug(data);
  if (data.message && typeof data.message === "string") {
    if (!data.styles) data.styles = new TextStyles("game start");
    handleConversation([data.message], [data.styles]);
    setGameID(data.game_id);
  }
};

export async function ply(
  gameID: string,
  userInput: string,
  gameOver: boolean,
  handleConversation: Function
) {
  if (gameOver) return null;

  const response = await fetch("http://127.0.0.1:5000/play/" + gameID, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: userInput }),
  });

  if (response.ok) {
    const data = await response.json();
    const command = castCommand(data.response);
    const text = extractTextContent(command);
    const styles = extractTextStyles(command);
    let uText = userInput ? ["\nYou: " + userInput].concat(text): text;
    let uStyles: TextStyles[] = [...Array(uText.length)].map(() => Object.assign(new TextStyles(), styles));
    handleConversation(uText, uStyles);

    return {
      command,
      styles,
      gameOver: command.is_game_over,
    };
  }
  return null;
}

export const validateOption = (
  lastMessage: any,
  userInput: string,
  handleConversation: Function
): boolean => {
  if (lastMessage?.type == "SelectOptionCommand" && userInput !== "") {
    let last: SelectOptionCommand = lastMessage as SelectOptionCommand;
    if (!last.options.some((tuple) => tuple.includes(userInput))) {
      let error = "Invalid option. Please try again.";
      handleConversation([error], [new TextStyles()]);
      return true;
    }
  }
  return false;
};