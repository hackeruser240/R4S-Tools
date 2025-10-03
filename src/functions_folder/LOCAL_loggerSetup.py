import os
import logging
from logging.handlers import RotatingFileHandler

def local_loggerSetup(logger,script_name):
    
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"LOGS-{script_name}.txt")
    logger.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File Handler with rotation
    file_handler = RotatingFileHandler(log_path, maxBytes=500_000, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    datefmt='%d-%b-%Y %I:%M %p'
    formatter = logging.Formatter( f"%(asctime)s [%(levelname)s] (%(name)s): %(message)s", datefmt=datefmt)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Attach handlers (avoid duplicates if re-imported)
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger