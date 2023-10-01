import { SendHorizonal } from "lucide-react";

function InputField() {
  return (
    <div className="flex justify-between gap-2 border w-[85vw] self-center mt-10 shadow-ctr2xl rounded-xl">
      <input
        className="rounded-xl p-3 w-full focus:outline-none"
        placeholder="Type your message..."
      />
      <button className="bg-transparent p-3 rounded-r-xl focus:outline-none">
        <SendHorizonal size={22} />
      </button>{" "}
    </div>
  );
}
export default InputField;
