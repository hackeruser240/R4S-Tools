from logging.handlers import RotatingFileHandler

import logging
import os
import inspect

def app_loggerSetup():
    # Dynamically get the caller module name
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_name = module.__name__ if module else "unknown"

    logger = logging.getLogger(module_name)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        os.makedirs("logs", exist_ok=True)

        # File handler (unchanged)
        file_handler = RotatingFileHandler(
            "logs/LOGS-app.log", maxBytes=1_000_000, backupCount=4, encoding="utf-8"
        )

        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
            datefmt="%d-%b-%Y %I:%M %p"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler (new)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
            datefmt="%d-%b-%Y %I:%M %p"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger