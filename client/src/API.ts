import { Dispatch, SetStateAction } from "react";
import {
  BaseCommand,
  SelectOptionCommand,
  castCommand,
  extractTextContent,
  extractTextStyles,
} from "./Command";
import { TextStyles } from "./components/Typewriter";

export interface SGProps {
  handleConversation: Function;
  setGameID: Dispatch<SetStateAction<string>>;
  handleUserInput: Function;
}

const fetchGame = async (url: string, gameID: string, userIn: string = "") => {
  return fetch(url + gameID, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: userIn }),
  });
};

export const loadGame = async (props: SGProps) => {
  console.log("[LOADING GAME]", localStorage.getItem("game_id"));
  let gameID = localStorage.getItem("game_id") as string;
  props.setGameID(gameID);
  const loadedGame = await fetchGame("http://127.0.0.1:5000/load/", gameID);

  if (!loadedGame.ok) {
    console.log("[RESPONSE NOT OK, RESTARTING GAME]");
    localStorage.removeItem("game_id");
    await startGame(props);
    return;
  }

  const data = await loadedGame.json();
  console.log("[RESPONSE OK, SETTING CONVERSATION As]", data);

  data.response.forEach((response: any) => {
    var {uText, uStyles} = processResponse(response);
    props.handleConversation(uText, uStyles);
  });
  if (data.length && !data[data.length - 1].expects_user_input) {
    props.handleUserInput("");
  }
};

export const startGame = async (props: SGProps) => {
  // If there is a game id in local storage, load that game
  console.log("[STARTING GAME]");
  if (localStorage.getItem("game_id")) {
    console.log(
      "[GAME ID FOUND AT LOCAL STORAGE]",
      localStorage.getItem("game_id")
    );
    loadGame(props);
    return;
  }

  // Otherwise, start a new game
  const response = await fetch("http://127.0.0.1:5000/start");

  if (!response.ok) {
    console.log("[RESPONSE NOT OK]");
    return;
  }
  console.log("[RESPONSE OK]");
  const data = await response.json();
  console.debug(data);
  if (data.message && typeof data.message === "string") {
    if (!data.styles) data.styles = new TextStyles("game start");
    console.log("[SETTING GAME_ID AND CONVERSATION]");
    props.handleConversation([data.message], [data.styles]);
    props.setGameID(data.game_id);
    localStorage.setItem("game_id", data.game_id);
  }
};

export async function ply(
  gameID: string,
  userInput: string,
  gameOver: boolean,
  handleConversation: Function
) {
  if (gameOver) return null;
  console.log("[PLYING]: ", userInput);
  const response = await fetchGame(
    "http://127.0.0.1:5000/play/",
    gameID,
    userInput
  );

  if (response.ok) {
    const data = await response.json();
    var { uText, uStyles, command, styles } = processResponse(data.response, userInput);
    handleConversation(uText, uStyles);
    return { command, styles, gameOver: command.is_game_over };
  }
  return null;
}

const processResponse = (data: any, userInput: string = "") => {
  console.log("[PROCESSING RESPONSE]: ", data);
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
    let last: SelectOptionCommand = lastMessage as SelectOptionCommand;
    if (!last.options.some((tuple) => tuple.includes(userInput))) {
      let error = "Invalid option. Please try again.";
      handleConversation([error], [new TextStyles()]);
      return true;
    }
  }
  return false;
};
