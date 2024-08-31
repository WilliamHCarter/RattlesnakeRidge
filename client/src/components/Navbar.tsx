import MobileMenu from "./MobileMenu";
import SourceButton from "./SourceButton";
import ThemeButton from "./ThemeButton";

function Navbar({ fullscreen }: { readonly fullscreen: boolean }) {
  return (
    <div className="flex w-[100vw] justify-between px-4 py-4">
      <h1 className="tablet:text-3xl text-2xl self-center font-semibold">Rattlesnake Ridge</h1>
      <nav className="flex gap-6 items-center">
        <div className="tablet:flex hidden gap-4">
          <SourceButton />
          <ThemeButton />
        </div>
        <div className="flex tablet:hidden gap-4">
          <ThemeButton />
          <MobileMenu fullscreen={fullscreen}/>
        </div>
      </nav>
    </div>
  );
}
export default Navbar;
