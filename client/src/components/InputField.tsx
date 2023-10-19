import { useState } from "react";
import { SendHorizontal, Loader2 } from "lucide-react";

type InputFieldProps = {
  onSend: (message: string) => void;
  disabled?: boolean;
};

function InputField({ onSend, disabled }: InputFieldProps) {
  const [input, setInput] = useState("");

  const handleSendClick = () => {
    if (!disabled && input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  return (
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
  );
}

export default InputField;
