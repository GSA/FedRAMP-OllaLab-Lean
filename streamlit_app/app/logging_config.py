# logging_config.py

"""
Modified logging_config.py

Defines logging configurations for the application.
Sets log levels, formats, handlers, and destinations (e.g., file, console, custom handlers).

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

# Import custom handlers
from logging_handlers import EmailAlertHandler, SlackAlertHandler, DatabaseLogHandler

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
    email_alerts: bool = False,
    email_config: dict = None,
    slack_alerts: bool = False,
    slack_webhook_url: str = None,
    database_logging: bool = False,
    database_log_path: str = 'logs/logs.db',
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
        email_alerts (bool):
            Enable or disable email alerts for critical errors.
        email_config (dict):
            Configuration for email alerts.
            Example:
            {
                'mailhost': 'smtp.example.com',
                'fromaddr': 'alerts@example.com',
                'toaddrs': ['admin@example.com'],
                'subject': 'Application Error Alert',
                'credentials': ('user', 'password'),
                'secure': ()
            }
        slack_alerts (bool):
            Enable or disable Slack alerts for errors.
        slack_webhook_url (str):
            The Slack webhook URL to send messages to.
        database_logging (bool):
            Enable or disable logging to a database.
        database_log_path (str):
            Path to the database file for logging.

    Raises:
        LoggingConfigurationError:
            If an error occurs during logging setup.

    Dependencies:
        - Standard logging library.
        - os, sys, datetime modules.
        - logging_handlers module for custom handlers.

    Example:
        setup_logging(
            email_alerts=True,
            email_config={
                'mailhost': 'smtp.example.com',
                'fromaddr': 'alerts@example.com',
                'toaddrs': ['admin@example.com'],
                'subject': 'Application Error Alert',
                'credentials': ('user', 'password'),
                'secure': ()
            },
            slack_alerts=True,
            slack_webhook_url='https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXX',
            database_logging=True,
            database_log_path='logs/logs.db',
        )
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

        # Create a list for handlers
        handlers = [console_handler, file_handler]

        # Add EmailAlertHandler if email alerts are enabled
        if email_alerts and email_config:
            email_handler = EmailAlertHandler(
                mailhost=email_config.get('mailhost'),
                fromaddr=email_config.get('fromaddr'),
                toaddrs=email_config.get('toaddrs'),
                subject=email_config.get('subject'),
                credentials=email_config.get('credentials', None),
                secure=email_config.get('secure', None)
            )
            email_handler.setLevel(logging.ERROR)
            email_handler.setFormatter(standard_formatter)
            handlers.append(email_handler)

        # Add SlackAlertHandler if Slack alerts are enabled
        if slack_alerts and slack_webhook_url:
            slack_handler = SlackAlertHandler(
                webhook_url=slack_webhook_url,
                level=logging.ERROR
            )
            slack_handler.setFormatter(standard_formatter)
            handlers.append(slack_handler)

        # Add DatabaseLogHandler if database logging is enabled
        if database_logging:
            db_handler = DatabaseLogHandler(
                db_path=database_log_path,
                level=log_level
            )
            db_handler.setFormatter(standard_formatter)
            handlers.append(db_handler)

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Capture all levels; handlers will filter

        # Remove any existing handlers
        logger.handlers = []

        # Add handlers to the root logger
        for handler in handlers:
            logger.addHandler(handler)

        # Optionally, configure module-specific loggers
        # For example, set different log levels for different modules
        # logger_module = logging.getLogger('table2json_extractor')
        # logger_module.setLevel(logging.DEBUG)

        # Silence noisy loggers from third-party libraries if necessary
        # logging.getLogger('some_noisy_library').setLevel(logging.WARNING)

    except Exception as e:
        # Raise a custom exception if logging setup fails
        raise LoggingConfigurationError(f"Failed to configure logging: {e}")