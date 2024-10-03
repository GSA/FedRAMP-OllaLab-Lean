# config.py

import os
import yaml
import logging

class ConfigManager:
    """
    Singleton class to manage application configuration.
    """
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False  # To prevent re-initialization
        return cls._instance

    def __init__(self, config_file='config.yaml'):
        if self._initialized:
            return  # Avoid re-initialization
        self.config_file = config_file
        self.config = {}
        self._initialized = True
        self.load_config()

    def load_config(self):
        """
        Load configuration from the YAML file.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                logging.info(f"Configuration loaded from '{self.config_file}'.")
            else:
                self.create_default_config()
                logging.info(f"Default configuration created at '{self.config_file}'.")
        except Exception as e:
            error_message = f"Error loading configuration: {str(e)}"
            logging.error(error_message)
            raise e

    def save_config(self):
        """
        Save the current configuration to the YAML file.
        """
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f)
            logging.info(f"Configuration saved to '{self.config_file}'.")
        except Exception as e:
            error_message = f"Error saving configuration: {str(e)}"
            logging.error(error_message)
            raise e

    def create_default_config(self):
        """
        Create a default configuration file with initial settings.
        """
        self.config = {
            'data_import': {
                'supported_formats': ['.csv', '.json', '.xlsx', '.xls', '.xml', '.parquet', '.tsv'],
                'default_encoding': 'utf-8',
            },
            'data_mapping': {
                'mapping_version': 1,
            },
            'data_normalization': {
                'scaling_methods': ['Min-Max Scaling (0-1)', 'Z-score Normalization'],
            },
            'data_deduplication': {
                'similarity_threshold': 0.8,
            },
            'data_validation': {
                'allowed_statuses': ['Active', 'Inactive', 'Pending'],
            },
            'logging': {
                'log_level': 'INFO',
                'log_file': 'logs/app.log',
            },
            'database': {
                'connection_string': '',
            },
            'audit_trail': {
                'audit_file': 'logs/audit.log',
            },
        }
        self.save_config()

    def get(self, section, key, default=None):
        """
        Retrieve a configuration value.

        :param section: The configuration section.
        :param key: The key within the section.
        :param default: Default value if key is not found.
        :return: The configuration value.
        """
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """
        Set a configuration value and save the configuration.

        :param section: The configuration section.
        :param key: The key within the section.
        :param value: The value to set.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        logging.info(f"Configuration '{section}.{key}' set to '{value}'.")
