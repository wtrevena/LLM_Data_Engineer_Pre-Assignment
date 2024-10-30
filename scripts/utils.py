# scripts/utils.py

import logging
from config import LOG_FILE

def get_logger(name):
    """
    Create and configure a logger for logging messages.

    Args:
        name (str): The name of the logger.

    Returns:
        Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a file handler for logging to a file
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)

    # Define the logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger if not already added
    if not logger.handlers:
        logger.addHandler(fh)

    return logger
