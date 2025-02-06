# app/anydoc_2_json/logger_manager.py

import logging
import os
import traceback

###
# To integrate LoggerManager into the existing system, other modules should import this class and replace any existing logging configurations with instances of LoggerManager.
###

class LoggerManager:
    """
    LoggerManager class for managing logging configuration, capturing system events, errors,
    and user activities, and logging them to files and console as per program requirements.

    Dependencies:
        - Built-in `logging` module for logging functionalities.
        - Built-in `os` module for file system interactions.
        - Built-in `traceback` module for exception traceback extraction.

    Upstream functions:
        - Any function or module in the system that requires logging should use this class.

    Downstream functions:
        - `setup_logger`
        - `log_info`
        - `log_warning`
        - `log_error`
        - `log_critical`
        - `log_exception`
        - `log_event`

    """

    def __init__(self, log_file_path: str, log_level: int = logging.INFO):
        """
        Initialize the LoggerManager instance.

        Parameters:
            log_file_path (str):
                The full path to the log file where logs will be saved.
            log_level (int, optional):
                The logging level threshold (e.g., logging.INFO, logging.DEBUG). Defaults to logging.INFO.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the log directory does not exist and cannot be created.
            PermissionError:
                If the program lacks permissions to create the log directory or write to the log file.

        Dependencies:
            - `os.makedirs` to create directories if they do not exist.
            - `logging.getLogger` to get a logger instance.
            - `self.setup_logger` to set up the logger with handlers and formatters.

        Upstream functions:
            - Constructor called by modules requiring logging.

        Downstream functions:
            - `setup_logger`

        """
        self.log_file_path = log_file_path
        self.log_level = log_level
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)

        # Ensure the directory for log files exists
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                raise FileNotFoundError(f"Cannot create log directory '{log_dir}': {e}")

        self.setup_logger()

    def setup_logger(self):
        """
        Set up the logger with a file handler and a console handler, including formatting.

        Parameters:
            None

        Returns:
            None

        Raises:
            IOError:
                If the log file cannot be opened for writing.
            ValueError:
                If an invalid log level is specified.

        Dependencies:
            - `logging.FileHandler` to handle logging to a file.
            - `logging.StreamHandler` to handle logging to the console.
            - `logging.Formatter` to format the log messages.

        Upstream functions:
            - `__init__`

        Downstream functions:
            - None

        """
        # Remove any existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Create file handler which logs to file
        try:
            fh = logging.FileHandler(self.log_file_path)
            fh.setLevel(self.log_level)
        except Exception as e:
            raise IOError(f"Failed to open log file '{self.log_file_path}' for writing: {e}")

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)  # Console handler logs ERROR and above

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_logger(self) -> logging.Logger:
        """
        Retrieve the configured logger instance for use in other modules.

        Parameters:
            None

        Returns:
            logging.Logger:
                The configured logger instance ready for logging messages.

        Raises:
            None

        Dependencies:
            - Returns the `self.logger` instance.

        Upstream functions:
            - Modules that need to log messages.

        Downstream functions:
            - None

        """
        return self.logger

    def log_info(self, message: str):
        """
        Log an informational message.

        Parameters:
            message (str):
                The informational message to log.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `self.logger.info` to log the informational message.

        Upstream functions:
            - Functions or methods that need to log info-level messages.

        Downstream functions:
            - None

        """
        self.logger.info(message)

    def log_warning(self, message: str):
        """
        Log a warning message.

        Parameters:
            message (str):
                The warning message to log.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `self.logger.warning` to log the warning message.

        Upstream functions:
            - Functions or methods that need to log warning-level messages.

        Downstream functions:
            - None

        """
        self.logger.warning(message)

    def log_error(self, message: str):
        """
        Log an error message.

        Parameters:
            message (str):
                The error message to log.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `self.logger.error` to log the error message.

        Upstream functions:
            - Functions or methods that need to log error-level messages.

        Downstream functions:
            - None

        """
        self.logger.error(message)

    def log_critical(self, message: str):
        """
        Log a critical error message indicating a severe problem.

        Parameters:
            message (str):
                The critical error message to log.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `self.logger.critical` to log the critical message.

        Upstream functions:
            - Functions or methods that need to log critical-level messages.

        Downstream functions:
            - None

        """
        self.logger.critical(message)

    def log_exception(self, exception: Exception, context_message: str = "", file_name: str = ""):
        """
        Log an exception with detailed traceback and context.

        Parameters:
            exception (Exception):
                The exception instance to log.
            context_message (str, optional):
                Additional context about where or why the exception occurred. Defaults to empty string.
            file_name (str, optional):
                Name of the file being processed when the exception occurred. Defaults to empty string.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `traceback.format_exc` to get the exception traceback.
            - `self.logger.error` to log the error with traceback.

        Upstream functions:
            - Exception handlers in other modules that catch exceptions.

        Downstream functions:
            - None

        """
        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = traceback.format_exc()
        log_message = (
            f"{context_message}\n"
            f"File: {file_name}\n"
            f"Exception type: {error_type}\n"
            f"Exception message: {error_message}\n"
            f"Stack trace:\n{stack_trace}"
        )
        self.logger.error(log_message)

    def log_event(self, event_message: str):
        """
        Log a general event message, such as user activities or system events.

        Parameters:
            event_message (str):
                The event message to log.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - `self.logger.info` to log the event message.

        Upstream functions:
            - Functions or methods that need to log general events or activities.

        Downstream functions:
            - None

        """
        self.logger.info(event_message)