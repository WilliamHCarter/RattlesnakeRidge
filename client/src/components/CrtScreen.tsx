import { useRef } from "react";
import AsciiBanner from "./AsciiBanner";
import Typewriter, { TextStyles } from "./Typewriter";
import "../index.css";

type CrtScreenProps = {
  conversation: string[];
  style: TextStyles[];
  onTypeState: (typing: boolean) => void;
};

function CrtScreen({ conversation, style, onTypeState }: CrtScreenProps) {
  //Control auto scroll
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const handleTyping = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  return (
    <div className="z-10 overflow-hidden flex justify-center self-center w-[85vw] pc:w-[70vw] h-[65vh] rounded-xl relative">
      <div className="z-7 rounded-xl absolute h-full w-full bg-gradient-radial from-[#063938] dark:from-[#042625] to-[#0c1919]" />
      <div
        className="CRT Filter rounded-xl"
        style={{
          pointerEvents: "none",
          overflow: "hidden",
          position: "absolute",
          zIndex: 11,
          width: "100%",
          height: "100%",
          opacity: "60%",
          background:
            "linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))",
          backgroundSize: "100% 3px, 6px 100%",
        }}
      />
      <div
        className="h-[100px] absolute w-full z-10 opacity-30 dark:opacity-20"
        style={{
          background:
            "linear-gradient( 0deg, rgba(0, 0, 0, 0) 0%, rgba(255, 255, 255, 0.2) 10%, rgba(0, 0, 0, 0.1) 100% )",
          animation: "scanline 6s linear infinite",
        }}
      ></div>
      <div
        className=" text-green-600 text-warp text-xs tablet:text-base font-mono p-8 z-10 overflow-auto overflow-x-hidden"
        ref={scrollRef}
      >
        <AsciiBanner>
          <Typewriter
            conversation={conversation}
            onMessageUpdate={handleTyping}
            style={style}
            onTypeState={onTypeState}
          />
        </AsciiBanner>
      </div>
    </div>
  );
}

export default CrtScreen;
