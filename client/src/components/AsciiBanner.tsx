import { useEffect, useRef, useState } from 'react';
import '../index.css';
function AsciiBanner({children}: {children: React.ReactNode }) {
  const asciiRef = useRef<HTMLDivElement>(null);
  const [asciiWidth, setAsciiWidth] = useState(0);

  const updateWidth = () => {
    if (asciiRef.current) {
      setAsciiWidth(asciiRef.current.offsetWidth);
    }
  };

  useEffect(() => {
    updateWidth();
    window.addEventListener("resize", updateWidth);

    return () => {
      window.removeEventListener("resize", updateWidth);
    };
  }, []);


  return (
    <div className=" ascii-banner w-full" ref={asciiRef}>
      <pre className=" pc:flex flex-col justify-center hidden ">
        <code className="leading-[1.4rem] ">
          +--------------------------------- Rattlesnake Ridge ----------------------------------+<br/>
          |                                                                                      |<br/>
          |          /\                     /\             /\          /\                 /\     |<br/>
          |        /    \         /\      /    \   _      /   \      /    \      /\      /   \   |<br/>
          |      _/\/\  / \      /   \   /\/\   /\/ \   _/      \  /       /\   /   \ _/      \  |<br/>
          |    _/     \/   \    /      \/    \ /   \ \/   /\     \/   /\  /  \ /               \ |<br/>
          |  _/              \/               v     \/   /  \/\/\    /  \/                       |<br/>
          | /                                        \  /        \/\/                            |<br/>
          |                                           \/                                         |<br/>
          |                                                                                      |<br/>
          |                       ____||____                     ____||____                      |<br/>
          |                      ///////////\                   ///////////\                     |<br/>
          |                     ///////////  \                 ///////////  \                    |<br/>
          |                    |    _    |    |               |    _    |    |                   |<br/>
          |                    |[] | | []| [] |               |[] | | []| [] |                   |<br/>
          |                    |___|_|___|____|               |___|_|___|____|                   |<br/>
          |                                                                                      |<br/>
          |                  The town of hidden truths, waiting to be unraveled..                |<br/>
          +--------------------------------------------------------------------------------------+<br/>
        </code>
      </pre>
      <pre className=" justify-center laptop:flex pc:hidden hidden ">
        <code className="leading-[1.4rem]">
          +---------------------------- Rattlesnake Ridge -----------------------------+<br/>
          |                                                                            |<br/>
          |     /\                     /\             /\          /\                 /\|<br/>
          |   /    \         /\      /    \   _      /   \      /    \      /\      /  |<br/>
          | _/\/\  / \      /   \   /\/\   /\/ \   _/      \  /       /\   /   \ _/    |<br/>
          |/     \/   \    /      \/    \ /   \ \/   /\     \/   /\  /  \ /            |<br/>
          |             \/               v     \/   /  \/\/\    /  \/                  |<br/>
          |                                     \  /        \/\/                       |<br/>
          |                                      \/                                    |<br/>
          |                                                                            |<br/>
          |                  ____||____                     ____||____                 |<br/>
          |                 ///////////\                   ///////////\                |<br/>
          |                ///////////  \                 ///////////  \               |<br/>
          |               |    _    |    |               |    _    |    |              |<br/>
          |               |[] | | []| [] |               |[] | | []| [] |              |<br/>
          |               |___|_|___|____|               |___|_|___|____|              |<br/>
          |                                                                            |<br/>
          |             The town of hidden truths, waiting to be unraveled..           |<br/>
          +----------------------------------------------------------------------------+<br/>
        </code>
      </pre>
      <pre className="flex justify-center laptop:hidden ">
        <code className="leading-[1rem]">
          +-------------------- Rattlesnake Ridge --------------------+<br/>
          |                                                           |<br/>
          |          /\                     /\             /\         |<br/>
          |        /    \         /\      /    \   _      /   \      /|<br/>
          |      _/\/\  / \      /   \   /\/\   /\/ \   _/      \  /  |<br/>
          |    _/     \/   \    /      \/    \ /   \ \/   /\     \/   |<br/>
          |  _/              \/               v     \/   /  \/\/\     |<br/>
          | /                                        \  /        \/\  |<br/>
          |                                           \/              |<br/>
          |                                                           |<br/>
          |                 `'::.                                     |<br/>
          |          _________H ,%%&%,                                |<br/>
          |         /\     _   \%&&%%&%                               |<br/>
          |        /  \___/^\___\%&%%&&                               |<br/>
          |        |  | []   [] |%\Y&%'                               |<br/>
          |        |  |   .-.   | ||                                  |<br/>
          |~~~~~~~~@._|@@_|||_@@|~||~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|<br/>
          |           `""") )"""`                                     |<br/>
          |                                                           |<br/>
          |                                                           |<br/>
          +-----------------------------------------------------------+<br/>
        </code>
      </pre>
      <div style={{ maxWidth: asciiWidth }}>
        {children}
      </div>
    </div>
  );
}

export default AsciiBanner;
