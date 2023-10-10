import { useState } from "react";
import { SendHorizonal } from "lucide-react";

type InputFieldProps = {
    onSend: (message: string) => void;
}

function InputField({ onSend }: InputFieldProps) {
        const [input, setInput] = useState('');
    
        const handleSendClick = () => {
            if (input.trim()) {
                onSend(input);
                setInput('');
            }
        };
        
    return (
        <div className="flex justify-between gap-2 border dark:border-dbutton bg:white dark:bg-dbutton w-[85vw] pc:w-[60vw] self-center mt-10 shadow-ctr2xl rounded-xl">
            <input
                className="rounded-xl p-3 w-full bg-transparent focus:outline-none"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />
            <button
                className="bg-transparent p-3 rounded-r-xl focus:outline-none"
                onClick={handleSendClick}
            >
                <SendHorizonal size={22} />
            </button>{" "}
        </div>
    );
}

export default InputField;
