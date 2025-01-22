# test_logging_config.py

"""
Unit tests for logging_config.py

Tests the setup_logging function to ensure that logging is configured correctly.
"""

import unittest
import logging
import os
import tempfile
import shutil
from logging.handlers import RotatingFileHandler

# Import the setup_logging function and custom exception
from logging_config import setup_logging, LoggingConfigurationError

class TestLoggingConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for logs
        self.test_log_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.test_log_dir, 'app.log')

    def tearDown(self):
        # Remove the temporary directory after tests
        shutil.rmtree(self.test_log_dir)

    def test_setup_logging_defaults(self):
        """
        Test the default logging configuration.
        """
        # Call setup_logging with default parameters
        setup_logging(log_dir=self.test_log_dir)

        # Get the root logger
        logger = logging.getLogger()

        # Check that there are handlers attached to the logger
        self.assertTrue(len(logger.handlers) >= 2)

        # Log a test message
        test_message = "This is a test log message."
        logger.info(test_message)

        # Check that the log file exists
        self.assertTrue(os.path.exists(self.test_log_file))

        # Read the log file and verify the test message is logged
        with open(self.test_log_file, 'r', encoding='utf-8') as f:
            log_contents = f.read()
            self.assertIn(test_message, log_contents)

    def test_setup_logging_custom_parameters(self):
        """
        Test logging configuration with custom parameters.
        """
        custom_log_file = os.path.join(self.test_log_dir, 'custom_app.log')

        # Call setup_logging with custom parameters
        setup_logging(
            log_file_path=custom_log_file,
            log_level=logging.DEBUG,
            console_log_level=logging.ERROR,
            log_dir=self.test_log_dir,
            max_log_file_size=1024 * 1024,  # 1 MB
            backup_count=3
        )

        # Get the root logger
        logger = logging.getLogger()

        # Log messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.error("Error message")

        # Check that the custom log file exists
        self.assertTrue(os.path.exists(custom_log_file))

        # Read the log file and verify the messages
        with open(custom_log_file, 'r', encoding='utf-8') as f:
            log_contents = f.read()
            self.assertIn("Debug message", log_contents)
            self.assertIn("Info message", log_contents)
            self.assertIn("Error message", log_contents)

    def test_logging_configuration_error(self):
        """
        Test that LoggingConfigurationError is raised when an error occurs.
        """
        # Attempt to set up logging with an invalid log directory
        with self.assertRaises(LoggingConfigurationError):
            setup_logging(log_dir='/invalid/path/to/logs')

if __name__ == '__main__':
    unittest.main()