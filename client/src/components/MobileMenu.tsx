import { useState } from "react";
import { Github, Menu } from "lucide-react";
import SettingsCard from "./SettingsCard";

export default function MobileMenu({ fullscreen }: { readonly fullscreen: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const [settingsCardOpen, setSettingsCardOpen] = useState(false); // Add state for settings card

  const menuItems: any = [
    {
      label: "Github",
      href: "https://github.com/WilliamHCarter/RattlesnakeRidge",
      icon: Github,
    },
  ];

  return (
    <>
      {!fullscreen && (
        <button
          className="inline-flex items-center justify-center gap-x-1.5 rounded-md w-10 h-10 bg-button dark:bg-dbutton z-30"
          aria-label="Menu"
          onClick={() => setIsOpen(!isOpen)}
        >
          <Menu />
        </button>
      )}

      <div
        className={`absolute right-0 z-30 mt-12 mr-4 w-64 text-xs bg-white dark:bg-dbg leading-5 rounded-lg shadow-lg border dark:border-dbutton focus:outline-none transition-all duration-200 ease-in-out transform ${
          isOpen ? "opacity-100 scale-100" : "opacity-0 hidden scale-95"
        }`}
      >
        <div className="p-3">
          {menuItems.map((item: any) => {
            return (
              <a
                href={item.href}
                className="group relative flex gap-x-4 items-center gap-y-2 p-2 rounded-lg"
                key={item.label}
                onClick={(e) => {
                  if (item.onClick) {
                    e.preventDefault();
                    item.onClick();
                  }
                }}
              >
                <div className="flex items-center justify-center rounded-lg bg-gray-50 dark:bg-dbutton p-2">
                  <item.icon
                    className="h-5 w-5 text-gray-600 dark:text-white group-hover:text-indigo-600"
                    aria-hidden="true"
                  />
                </div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  {item.label}
                </div>
              </a>
            );
          })}
        </div>
      </div>
      {settingsCardOpen && (
        <div className="z-30">
          <SettingsCard onClose={() => setSettingsCardOpen(false)} />
        </div>
      )}
    </>
  );
}
