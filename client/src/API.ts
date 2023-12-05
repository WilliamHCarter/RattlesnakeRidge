import { Dispatch, SetStateAction } from "react";
import {
  SelectOptionCommand,
  castCommand,
  extractTextContent,
  extractTextStyles,
} from "./Command";
import { TextStyles } from "./components/Typewriter";

const BASE_URL = "http://127.0.0.1:5000/";

export interface SGProps {
  handleConversation: (text: string[], styles: TextStyles[]) => void;
  setGameID: Dispatch<SetStateAction<string>>;
  handleUserInput: (input: string) => void;
}

const fetchGame = async (
  endpoint: string,
  gameID: string,
  userIn: string = ""
) => {
  return fetch(`${BASE_URL}${endpoint}${gameID}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: userIn }),
  });
};

const getGameID = (): string => localStorage.getItem("game_id") as string;

export const loadGame = async (props: SGProps) => {
  const gameID = getGameID();
  props.setGameID(gameID);
  const loadedGame = await fetchGame("load/", gameID);

  if (!loadedGame.ok) {
    localStorage.removeItem("game_id");
    return false;
  }

  const data = await loadedGame.json();
  data.response.forEach((response: any) => {
    let { uText, uStyles } = processResponse(response);
    uStyles = uStyles.map((style) => ({ ...style, characterDelayMs: 0 }));
    props.handleConversation(uText, uStyles);
  });
  if (data.length && !data[data.length - 1].expects_user_input) {
    props.handleUserInput("");
  }
};

export const startGame = async (props: SGProps) => {
  const response = await fetch(`${BASE_URL}start`);

  if (!response.ok) {
    return;
  }
  const data = await response.json();
  console.debug(data);
  if (data.message && typeof data.message === "string") {
    if (!data.styles) data.styles = new TextStyles("game start");
    props.handleConversation([data.message], [data.styles]);
    props.setGameID(data.game_id);
    localStorage.setItem("game_id", data.game_id);
  }
};

export const endGame = async () => {
  const gameID = getGameID();
  return fetchGame("end/", gameID);
};

export async function ply(userInput: string, handleConversation: Function) {
  const gameID = getGameID();
  const response = await fetchGame("play/", gameID, userInput);

  if (response.ok) {
    const data = await response.json();
    let { uText, uStyles, command, styles } = processResponse(
      data.response,
      userInput
    );
    handleConversation(uText, uStyles);
    return { command, styles, gameOver: command.is_game_over };
  }
  return null;
}

const processResponse = (data: any, userInput: string = "") => {
  const command = castCommand(data);
  const text = extractTextContent(command);
  const styles = extractTextStyles(command);
  let uText = userInput ? ["\nYou: " + userInput].concat(text) : text;
  let uStyles: TextStyles[] = [...Array(uText.length)].map(() =>
    Object.assign(new TextStyles(), styles)
  );
  return { uText, uStyles, command, styles };
};

export const validateOption = (
  lastMessage: any,
  userInput: string,
  handleConversation: Function
): boolean => {
  if (lastMessage?.type == "SelectOptionCommand" && userInput !== "") {
    const last: SelectOptionCommand = lastMessage as SelectOptionCommand;
    if (!last.options.some((tuple) => tuple.includes(userInput))) {
      const error = "Invalid option. Please try again.";
      handleConversation([error], [new TextStyles()]);
      return true;
    }
  }
  return false;
};
