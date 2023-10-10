import CrtScreen from "./components/CrtScreen";
import InputField from "./components/InputField";
import Navbar from "./components/Navbar";
import ResponseHandler from "./components/ResponseHandler";

function App() {
  return (
    <div className="mx-auto flex flex-col">
      <Navbar />
      <div className="Divider shrink-0 bg-[#e4e4e7] dark:bg-dbutton h-[1px] w-full" />
      <div className="py-4" />
      <ResponseHandler />
    </div>
  );
}

export default App;
