# utils/logging_utils.py

import logging
import os

def configure_logging(log_level=logging.INFO, log_file='logs/data_unificator_app.log'):
    """
    Configure logging settings.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_event(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
