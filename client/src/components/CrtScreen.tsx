function CrtScreen({conversation}: {conversation: string[]}) {
  return (
    <div className="flex self-center w-[85vw] pc:w-[70vw] h-[65vh] rounded-xl relative">
      <div className="rounded-xl absolute h-full w-full bg-gradient-radial from-[#063938] dark:from-[#042625] to-[#0c1919]" />
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
      <div className="text-lg text-green-600 font-mono p-4 z-10">
        Welcome to Rattlesnake Ridge...
        {conversation.map((message, index) => (
          <div key={index}>
            {"\n" +message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CrtScreen;
