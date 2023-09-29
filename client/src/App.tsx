import CrtScreen from "./components/CrtScreen";
import Navbar from "./components/Navbar";
function App() {
  return (
    <div className="mx-auto flex flex-col">
      <Navbar />
      <div className="py-4"/>
      <CrtScreen/>
    </div>
  );
}

export default App;
