import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]); // Explicitly declare the type as string[]
  const [gameID, setGameID] = useState<string>("");
  const [loaded, setLoaded] = useState(false);

  // Fetch the initial message from the server when the component mounts.
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://127.0.0.1:5000/start");
      if (response.ok && !loaded) {
        const data = await response.json();
        console.log(data);
        setConversation((prev) => [...prev, data.message]);
        setLoaded(true);
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

  // Send `userInput` to the server, receive response, then add to `conversation`.
  const handleUserInput = async (userInput: string) => {
    if (userInput != "") {
      setConversation((prev) => [...prev, "\nUser: " + userInput + "\n"]);
    }
    let data = await sendRequest(userInput);
    let message = data.response?.message ?? "";
    let options = (data.response?.options ?? []).map((option: any[]) =>
      option.join(": ")
    );

    if (data.response.expects_user_input == true) {
      setConversation((prev) => [...prev, message, ...options]);
    } else {
      handleUserInput("");
      setConversation((prev) => [...prev, message, ...options]);
    }
  };

  return (
    <div className="mx-auto flex flex-col">
      <CrtScreen conversation={conversation} />
      <InputField onSend={handleUserInput} />
    </div>
  );
}

export default ResponseHandler;
