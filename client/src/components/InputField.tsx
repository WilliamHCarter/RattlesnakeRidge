import React, { useState } from "react";
import { SendHorizontal, Loader2 } from "lucide-react";

type InputFieldProps = {
  onSend: (message: string) => void;
  newGame?: boolean;
  disabled?: boolean;
  gameOver?: boolean;
  onRestart?: () => void;
  isFullscreen?: boolean;
};

function InputField({ onSend, newGame, disabled, gameOver, onRestart, isFullscreen }: InputFieldProps) {
  const [input, setInput] = useState("");

  const handleSendClick = () => {
    if (!disabled && input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  // Style adjustments for fullscreen mode
  const fullscreenStyles: React.CSSProperties = isFullscreen ? {
    backgroundColor: 'transparent',
    color: '#16A34A',
    border: '2px solid #16A34A',
    position: 'absolute',
    bottom: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '80%',
    animation: 'borderWarp 0.15s infinite'
  } : {};

  const fullscreenButtonStyles: React.CSSProperties = isFullscreen ? {
    backgroundColor: 'transparent',
    color: '#16A34A',
    border: '2px solid #16A34A',
    position: 'absolute',
    bottom: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    animation: 'textWarp 0.15s infinite, borderWarp 0.15s infinite'
  } : {};

  if (newGame) {
    return (
      <div className="flex justify-center mt-6 z-0">
        <button
          onClick={onRestart}
          className="bg-black dark:bg-dbutton text-white rounded-md py-2 px-5"
          style={fullscreenButtonStyles}
        >
          Start Game
        </button>
      </div>
    );
  }

  return !gameOver ? (
    <div
      className={`flex justify-between gap-2 border dark:border-dbutton bg-white dark:bg-dbutton w-[85vw] pc:w-[60vw] self-center mt-10 shadow-ctr2xl rounded-xl ${
        disabled ? "bg-opacity-80" : ""
      }`}
      style={fullscreenStyles}
    >
      <input
        className={`rounded-xl p-3 w-full bg-transparent focus:outline-none ${isFullscreen ? 'placeholder-green-600 text-warp' : ''}`}
        placeholder={disabled ? "" : "Type your message..."}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) =>
          e.key === "Enter" && !disabled ? handleSendClick() : null
        }
      />
      <button
        className="bg-transparent p-3 rounded-r-xl focus:outline-none"
        onClick={handleSendClick}
        disabled={disabled}
      >
        {disabled ? (
          <Loader2 className="animate-spin" size={22} />
        ) : (
          <SendHorizontal size={22} />
        )}
      </button>
    </div>
  ) : (
    <div className="flex justify-center mt-6">
      <button
        onClick={onRestart}
        className="bg-black dark:bg-dbutton text-white rounded-md py-2 px-5"
        style={fullscreenButtonStyles}
      >
        Play Again
      </button>
    </div>
  );
}

export default InputField;
