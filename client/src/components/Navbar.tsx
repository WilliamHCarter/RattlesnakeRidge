import SettingsButton from "./SettingsButton";

function Navbar() {
  return (
    <div className="flex w-[100vw] justify-between px-4 py-4">
      <h1 className="text-3xl font-semibold">Rattlesnake Ridge</h1>
      <nav className="flex gap-6 items-center">
        <SettingsButton />
      </nav>
    </div>
  );
}
export default Navbar;
