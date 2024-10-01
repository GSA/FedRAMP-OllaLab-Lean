# config.py

import os
import yaml
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action

class ConfigManager:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """
        Load configuration from the YAML file.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                    record_action(f"Configuration loaded from '{self.config_file}'.")
            else:
                self.create_default_config()
                record_action(f"Default configuration created at '{self.config_file}'.")
        except Exception as e:
            error_message = f"Error loading configuration: {str(e)}"
            log_error(error_message)
            raise e

    def save_config(self):
        """
        Save the current configuration to the YAML file.
        """
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f)
                record_action(f"Configuration saved to '{self.config_file}'.")
        except Exception as e:
            error_message = f"Error saving configuration: {str(e)}"
            log_error(error_message)
            raise e

    def create_default_config(self):
        """
        Create a default configuration file.
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
        Get a configuration value.
        """
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """
        Set a configuration value.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        record_action(f"Configuration '{section}.{key}' set to '{value}'.")
