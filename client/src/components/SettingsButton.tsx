import { Settings } from "lucide-react";

function SettingsButton() {
  return (
    <button className="flex gap-2 items-center hover:bg-neutral p-2 bg-white rounded-md">
      <Settings size={24} />
    </button>
  );
}

export default SettingsButton;
