import { Dispatch, SetStateAction } from "react";
import { castCommand, extractTextContent, extractTextStyles } from "./Command";
import { TextStyles } from "./components/Typewriter";

interface SGProps {
  setConversation: Dispatch<SetStateAction<string[]>>;
  setGameID: Dispatch<SetStateAction<string>>;
  setStyles: Dispatch<SetStateAction<TextStyles>>;
  isMounted: () => boolean;
}

export const startGame = async ({
  setConversation,
  setGameID,
  setStyles,
  isMounted,
}: SGProps) => {
  const response = await fetch("http://127.0.0.1:5000/start");

  if (!response.ok || !isMounted()) {
    return;
  }

  const data = await response.json();
  const command = castCommand(data.response);
  const styles = extractTextStyles(command);
  if (data.message && typeof data.message === "string") {
    setConversation((prev) => [...prev, data.message]);
    setGameID(data.game_id);
    setStyles(styles);
  }
};

export async function playGame(
  gameID: string,
  userInput: string,
  gameOver: boolean,
  setConversation: Function
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
    console.log(data);
    let uText = userInput ? "\nYou: " + userInput : "";
    setConversation((prev: string[]) => [...prev, uText, ...text]);

    return {
      command,
      styles,
      gameOver: command.is_game_over,
    };
  }
  return null;
}
