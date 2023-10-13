import React, { useEffect, useState } from 'react';

type TypewriterProps = {
  conversation: string[];
  onMessageUpdate: (message: string) => void;  // New prop to handle currentMessage updates
};

const Typewriter: React.FC<TypewriterProps> = ({ conversation, onMessageUpdate }) => {
  const [currentMessage, setCurrentMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (messageIndex < conversation.length) {
      if (charIndex < conversation[messageIndex].length) {
        const timeoutId = setTimeout(() => {
          const newMessage = currentMessage + conversation[messageIndex][charIndex];
          setCurrentMessage(newMessage);
          onMessageUpdate(newMessage);  
          setCharIndex((prev) => prev + 1);
        }, 50); // Adjust speed here

        return () => clearTimeout(timeoutId);
      } else {
        setCurrentMessage('');
        setMessageIndex((prev) => prev + 1);
        setCharIndex(0);
      }
    }
  }, [messageIndex, charIndex, conversation, currentMessage, onMessageUpdate]);  

  return (
    <div>
      {conversation.slice(0, messageIndex).map((message, index) => (
        <pre key={index} className="whitespace-pre-wrap">{message}</pre>
      ))}
      <pre className="whitespace-pre-wrap">{currentMessage}</pre>
    </div>
  );
};

export default Typewriter;
