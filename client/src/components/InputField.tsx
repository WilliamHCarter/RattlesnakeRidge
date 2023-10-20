import { useState } from "react";
import { SendHorizontal, Loader2 } from "lucide-react";

type InputFieldProps = {
  onSend: (message: string) => void;
  disabled?: boolean;
  gameOver?: boolean;
  onRestart?: () => void;
};

function InputField({
  onSend,
  disabled,
  gameOver,
  onRestart,
}: InputFieldProps) {
  const [input, setInput] = useState("");

  const handleSendClick = () => {
    if (!disabled && input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  return !gameOver ? (
    <div
      className={`flex justify-between gap-2 border dark:border-dbutton bg-white dark:bg-dbutton w-[85vw] pc:w-[60vw] self-center mt-10 shadow-ctr2xl rounded-xl ${
        disabled ? "bg-opacity-80" : ""
      }`}
    >
      <input
        className="rounded-xl p-3 w-full bg-transparent focus:outline-none"
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
      >
        Play Again
      </button>
    </div>
  );
}

export default InputField;
