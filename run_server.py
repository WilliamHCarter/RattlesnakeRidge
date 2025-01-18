import logging

from server import app

# Set up the default logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console logger
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(ch)

# Create a file logger with everything
fh = logging.FileHandler("server.log", mode="a", encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(fh)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
