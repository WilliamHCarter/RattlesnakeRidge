import { Dispatch, SetStateAction } from "react";
import {
  GenericMessageCommand,
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

const fetchGame = async (url: string, gameID: string) => {
  return fetch(url + gameID, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: "" }),
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

  for (let i in data) {
    var cmd = data[i];
    console.log("cmd: ", cmd);
    var text: string[] = [];
    var styles: TextStyles[] = [];
    var last: GenericMessageCommand | null = null;
    for (var idx in cmd) {
      console.log("idx: ", cmd[idx]);
      const command = castCommand(cmd[idx]) as GenericMessageCommand;
      command.character_delay_ms = 0;
      text.push(...extractTextContent(command));
      const s = extractTextStyles(command);
      let uStyles: TextStyles[] = [...Array(text.length)].map(() =>
        Object.assign(new TextStyles(), s)
      );
      styles.push(...uStyles);
      last = command;
    }
    props.handleConversation(text, styles);
    if (last && !last.expects_user_input) {
      props.handleUserInput("");
    }
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
  console.log("[NO GAME ID FOUND AT LOCAL STORAGE]");

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
  console.log("plying: ", userInput);
  const response = await fetch("http://127.0.0.1:5000/play/" + gameID, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: userInput }),
  });
  console.log("Testing: ", gameID);
  const tester = await fetch("http://127.0.0.1:5000/load/" + gameID, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: userInput }),
  });
  const remy = await tester.json();
  console.log("tester: \n", remy);

  if (response.ok) {
    const data = await response.json();
    const command = castCommand(data.response);
    const text = extractTextContent(command);
    const styles = extractTextStyles(command);
    let uText = userInput ? ["\nYou: " + userInput].concat(text) : text;
    let uStyles: TextStyles[] = [...Array(uText.length)].map(() =>
      Object.assign(new TextStyles(), styles)
    );
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
