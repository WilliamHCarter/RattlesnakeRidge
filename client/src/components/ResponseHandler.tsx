import { useEffect, useState } from "react";
import InputField from "./InputField";
import CrtScreen from "./CrtScreen";

function ResponseHandler() {
  const [conversation, setConversation] = useState<string[]>([]); // Explicitly declare the type as string[]
  const [gameID, setGameID] = useState<string>("");
  var loaded = false;
  
  // Fetch the initial message from the server when the component mounts.
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://127.0.0.1:5000/start");
      if (response.ok && !loaded) {
        const data = await response.json();
        console.log(data);
        setConversation((prev) => [...prev, data.message]);
        loaded = true;
        setGameID(() =>(data.game_id));
      } else {
      }
    };

    fetchData();
  }, []);

  // Send `userInput` to the server, receive response, then add to `conversation`.
  const handleUserInput = async (userInput: string) => {
    const response = await fetch("http://127.0.0.1:5000/play/"+gameID, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userInput: userInput }),
    });

    if (response.ok) {
      const data = await response.json();
      setConversation((prev) => [...prev, userInput, data.message]);
    } else {
      console.error("Failed to send the message");
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
