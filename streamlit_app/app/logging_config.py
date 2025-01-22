# logging_config.py

"""
logging_config.py

Defines logging configurations for the application.
Sets log levels, formats, handlers, and destinations (e.g., file, console).

This module provides a function `setup_logging()` to configure logging
for the entire application.

It is designed to be imported and called at the entry point of the application
before any logging is performed.

Example usage:
    from logging_config import setup_logging
    setup_logging()
"""

import logging
import logging.config
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LoggingConfigurationError(Exception):
    """
    Custom exception raised when an error occurs during logging configuration.
    """
    pass

def setup_logging(
    log_file_path: str = None,
    log_level: int = logging.INFO,
    console_log_level: int = logging.INFO,
    log_dir: str = "logs",
    max_log_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
):
    """
    Configures logging for the application.

    Parameters:
        log_file_path (str):
            The file path to write log files.
            If not specified, defaults to 'logs/app.log'.
        log_level (int):
            The logging level for file logs.
            Defaults to logging.INFO.
        console_log_level (int):
            The logging level for console logs.
            Defaults to logging.INFO.
        log_dir (str):
            The directory where log files will be stored.
            Defaults to 'logs'.
        max_log_file_size (int):
            The maximum size of a log file in bytes before it is rotated.
            Defaults to 10 MB.
        backup_count (int):
            The number of backup log files to keep when rotating.
            Defaults to 5.

    Raises:
        LoggingConfigurationError:
            If an error occurs during logging setup.

    Dependencies:
        - Standard logging library.
        - os, sys, datetime modules.

    Example:
        setup_logging()
    """

    try:
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set default log file path if not provided
        if log_file_path is None:
            log_file_path = os.path.join(log_dir, 'app.log')

        # Define log formatters
        standard_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            fmt='[%(levelname)s] %(message)s'
        )

        # Create console handler with specified log level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(simple_formatter)

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            mode='a',
            maxBytes=max_log_file_size,
            backupCount=backup_count,
            encoding='utf-8',
            delay=0
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(standard_formatter)

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Capture all levels; handlers will filter

        # Remove any existing handlers
        logger.handlers = []

        # Add handlers to the root logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Optionally, configure module-specific loggers
        # For example, set different log levels for different modules
        # logger_module = logging.getLogger('table2json_extractor')
        # logger_module.setLevel(logging.DEBUG)

        # Silence noisy loggers from third-party libraries if necessary
        # logging.getLogger('some_noisy_library').setLevel(logging.WARNING)

    except Exception as e:
        # Raise a custom exception if logging setup fails
        raise LoggingConfigurationError(f"Failed to configure logging: {e}")