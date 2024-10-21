# modules/data_normalization.py

import pandas as pd
from multiprocessing import Pool
import logging
from data_unificator.utils.normalization_utils import (
    standardize_formats,
    handle_data_types,
    standardize_units,
    detect_outliers,
    apply_outlier_handling,
    apply_scaling,
    aggregate_fields,
    remove_fields,
    standardize_encoding,
)
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action
import traceback

class DataNormalizer:
    def __init__(self, resolved_data):
        """
        Initialize the DataNormalizer with the resolved data from the previous step.
        """
        self.resolved_data = resolved_data  # List of dictionaries with keys: 'file', 'data'
        self.normalized_data = []
        self.user_actions = {}

    def standardize_data_formats(self):
        """
        Standardize data formats (dates, numbers, text casing).
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = standardize_formats(df)
                data['data'] = df
                record_action(f"Standardized formats in '{data['file']}'")
            log_event("Data formats standardized across all sources.")
        except Exception as e:
            error_message = f"Error standardizing data formats: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            raise e

    def handle_data_types(self):
        """
        Convert different data types into a unified format.
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = handle_data_types(df)
                data['data'] = df
                record_action(f"Handled data types in '{data['file']}'")
            log_event("Data types unified across all sources.")
        except Exception as e:
            error_message = f"Error handling data types: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def standardize_units_of_measurement(self):
        """
        Standardize units of measurement (time, currency, etc.).
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = standardize_units(df)
                data['data'] = df
                record_action(f"Standardized units in '{data['file']}'")
            log_event("Units of measurement standardized across all sources.")
        except Exception as e:
            error_message = f"Error standardizing units: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def detect_and_handle_outliers(self, user_selections):
        """
        Detect extreme outliers and allow user to select action.
        """
        try:
            for data in self.resolved_data:
                # Pass a list containing the single data dictionary
                outlier_info = detect_outliers([data])
                if outlier_info:
                    df = data['data']
                    # Extract the outliers for the current data source
                    current_outliers = outlier_info[0]['outliers']
                    df = apply_outlier_handling(df, current_outliers, user_selections)
                    data['data'] = df
                    record_action(f"Outliers handled in '{data['file']}' using {user_selections}")
            log_event("Outliers detected and handled across all sources.")
        except Exception as e:
            error_message = f"Error handling outliers: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def apply_scaling_to_fields(self, scaling_options):
        """
        Apply scaling to selected fields based on user options.
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = apply_scaling(df, scaling_options)
                data['data'] = df
                record_action(f"Applied scaling to fields in '{data['file']}'")
            log_event("Scaling applied to selected fields.")
        except Exception as e:
            error_message = f"Error applying scaling: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def aggregate_and_remove_fields(self, aggregation_options, fields_to_remove):
        """
        Aggregate new fields and remove selected fields.
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = aggregate_fields(df, aggregation_options)
                df = remove_fields(df, fields_to_remove)
                data['data'] = df
                record_action(f"Aggregated and removed fields in '{data['file']}'")
            log_event("Fields aggregated and removed as per user selections.")
        except Exception as e:
            error_message = f"Error aggregating or removing fields: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def standardize_text_encoding(self):
        """
        Standardize text encoding.
        """
        try:
            for data in self.resolved_data:
                df = data['data']
                df = standardize_encoding(df)
                data['data'] = df
                record_action(f"Standardized text encoding in '{data['file']}'")
            log_event("Text encoding standardized across all sources.")
        except Exception as e:
            error_message = f"Error standardizing text encoding: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def display_normalized_data(self):
        """
        Placeholder method to comply with the original interface.
        Actual display logic should be handled in the UI.
        """
        pass
