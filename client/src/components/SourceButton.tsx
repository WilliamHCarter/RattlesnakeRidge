function SourceButton() {
  return (
    <div className=" bg-neutral hover:bg-[#756e6e25] rounded-lg">
      <a
        className="flex items-center px-4 py-2"
        href="https://github.com/WilliamHCarter/RattlesnakeRidge"
        aria-label="Github"
      >
        <img
          className="inline-block w-4 mr-2 filter grayscale contrast-[8500] dark:invert"
          src="/github.svg"
          alt="gh-icon"
        />
        <p className="text-dark dark:text-offw text-base font-[500]">Source</p>
      </a>
    </div>
  );
}

export default SourceButton;
