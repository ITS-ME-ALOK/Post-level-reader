"""
Logger configuration for the application.
"""
import logging
import os
from datetime import datetime
from utils.constants import LOGS_DIR

def setup_logger() -> logging.Logger:
    """
    Configures and returns the application logger.
    """
    logger = logging.getLogger("PDFToExcelApp")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create file handler
        log_file_name = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        fh = logging.FileHandler(os.path.join(LOGS_DIR, log_file_name))
        fh.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to handlers
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger

# Global logger instance
logger = setup_logger()
