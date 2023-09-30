import { FC } from "react";
import { X } from "lucide-react";

interface SettingsCardProps {
  onClose: () => void;
}

const SettingsCard: FC<SettingsCardProps> = ({ onClose }) => {
  return (
    <>
      <div className="fixed inset-0 bg-white bg-opacity-50 flex justify-center items-center backdrop-blur-sm z-10" />
      <div className="fixed inset-0 flex justify-center items-center z-20">
        <div className="bg-white rounded-lg p-4 shadow-lg w-full max-w-lg">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold">Settings</h1>
            <button className="bg-white" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
          <div className="mt-6">
            <label className="block text-sm font-medium" htmlFor="apiKey">
              API Key
            </label>
            <input
              className="mt-1 p-2 w-full border rounded-md"
              type="text"
              id="apiKey"
            />
          </div>
          <div className="flex justify-end mt-6">
            <button className="bg-black text-white rounded-md py-2 px-4">
              Save
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default SettingsCard;
