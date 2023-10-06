import { Moon, Sun } from "lucide-react";
import { useState, useEffect } from "react";

function ThemeButton() {
  const [theme, setTheme] = useState<string>(
    localStorage.getItem("theme") ?? "light"
  );

  const toggleTheme = () => {
    setTheme((currentTheme) => (currentTheme === "light" ? "dark" : "light"));
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    const systemPreference = window.matchMedia("(prefers-color-scheme: dark)");

    if (!localStorage.getItem("theme")) {
      const prefersDark = systemPreference.matches ?? false;
      setTheme(prefersDark ? "dark" : "light");
    }

    const handleMediaChange = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? "dark" : "light");
    };

    systemPreference.addEventListener("change", handleMediaChange);
    return () =>
      systemPreference.removeEventListener("change", handleMediaChange);
  }, []);

  return (
    <button
      className="bg-button dark:bg-dbutton hover:bg-[#756e6e25] rounded-lg p-2"
      aria-label="Toggle Dark Mode"
      onClick={toggleTheme}
    >
      <Moon size={24} className="dark:hidden" /> 
      <Sun size={24} className="hidden dark:block"/> 
    </button>
  );
}
export default ThemeButton;
