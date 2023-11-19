import React, { useEffect, useState } from 'react';

export class TextStyles {
  message: string;
  doTypeMessage: boolean;
  characterDelayMs: number;

  constructor(
      message: string = "",
      doTypeMessage: boolean = true,
      characterDelayMs: number = 0,
  ) {
      this.message = message;
      this.doTypeMessage = doTypeMessage;
      this.characterDelayMs = characterDelayMs;
  }
}

type TypewriterProps = {
  conversation: string[];
  onMessageUpdate: (message: string) => void;
  style: TextStyles[];
  onTypeState: (typing: boolean) => void;
};

const Typewriter: React.FC<TypewriterProps> = ({ conversation, onMessageUpdate, style, onTypeState}) => {
  const [currentMessage, setCurrentMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (messageIndex < conversation.length) {
      onTypeState(true); // Typing starts
      const currentStyle = style[messageIndex] ?? new TextStyles();
      if (charIndex < conversation[messageIndex].length) {
        const timeoutId = setTimeout(() => {
          const newMessage = currentMessage + conversation[messageIndex][charIndex];
          setCurrentMessage(newMessage);
          onMessageUpdate(newMessage);  
          setCharIndex((prev) => prev + 1);
        }, currentStyle.characterDelayMs); 

        return () => clearTimeout(timeoutId);
      } else {
        setCurrentMessage('');
        setMessageIndex((prev) => prev + 1);
        setCharIndex(0);
      }
    } else {
      onTypeState(false); // Typing ends
    }
  }, [messageIndex, charIndex, conversation, currentMessage, onMessageUpdate, onTypeState]);  

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
