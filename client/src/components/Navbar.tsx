import SettingsButton from "./SettingsButton";
import SourceButton from "./SourceButton";
import ThemeButton from "./ThemeButton";

function Navbar() {
  return (
    <div className="flex w-[100vw] justify-between px-4 py-4">
      <h1 className="text-3xl font-semibold">Rattlesnake Ridge</h1>
      <nav className="flex gap-6 items-center">
        <div className="flex gap-4">
          <SourceButton />
          <ThemeButton />
          <SettingsButton />
        </div>
      </nav>
    </div>
  );
}
export default Navbar;
