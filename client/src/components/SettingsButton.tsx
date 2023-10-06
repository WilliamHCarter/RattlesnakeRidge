import { useState } from "react";
import { Settings } from "lucide-react";
import SettingsCard from "./SettingsCard";

function SettingsButton() {
  const [settingsCard, setSettingsCard] = useState(false);
  window.addEventListener('keydown', (e) => e.key === 'Escape' ? setSettingsCard(false) : null);

  return (
    <>
      <button
        className="p-2 bg-transparent rounded-md transition-all duration-150 ease-in-out hover:bg-neutral hover:shadow-sm"
        onClick={() => setSettingsCard(true)}
      >
        <Settings size={24} />
      </button>

      {settingsCard && (
        <div className="z-30">
          <SettingsCard onClose={() => setSettingsCard(false)} />
        </div>
      )}
    </>
  );
}

export default SettingsButton;
