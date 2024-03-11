import { useState } from "react";
import Navbar from "./components/Navbar";
import ResponseHandler from "./components/ResponseHandler";

function App() {
  const [fullscreen, setFullscreen] = useState(false);
  return (
    <div className="mx-auto flex flex-col">
      <Navbar fullscreen={fullscreen}/>
      <div className="Divider shrink-0 bg-[#e4e4e7] dark:bg-dbutton h-[1px] w-full" />
      <div className="py-4" />
      <ResponseHandler setFullscreen={setFullscreen} />
    </div>
  );
}

export default App;
