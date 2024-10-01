# utils/logging_utils.py

import logging
import os
from data_unificator.config import ConfigManager

config_manager = ConfigManager()

log_level = getattr(logging, config_manager.get('logging', 'log_level', 'INFO').upper(), logging.INFO)
log_file = config_manager.get('logging', 'log_file', 'logs/app.log')

logging.basicConfig(
    filename=log_file,
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_event(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
