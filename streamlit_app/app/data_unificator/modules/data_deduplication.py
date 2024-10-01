# modules/data_deduplication.py

import pandas as pd
from multiprocessing import Pool
from data_unificator.utils.deduplication_utils import (
    detect_duplicates,
    eliminate_duplicates,
    merge_datasets,
    save_consolidated_data,
)
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action
import traceback

class DataDeduplicator:
    def __init__(self, normalized_data):
        """
        Initialize the DataDeduplicator with the normalized data.
        """
        self.normalized_data = normalized_data  # List of dictionaries with keys: 'file', 'data'
        self.consolidated_data = None
        self.duplicate_criteria = []
        self.user_actions = {}

    def merge_data(self):
        """
        Merge data from multiple sources into a single dataset.
        """
        try:
            dataframes = [data['data'] for data in self.normalized_data]
            self.consolidated_data = merge_datasets(dataframes)
            record_action("Merged data from multiple sources.")
            log_event("Data merged successfully.")
        except Exception as e:
            error_message = f"Error merging data: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            raise e

    def configure_duplicate_detection(self, criteria):
        """
        Configure criteria for duplicate detection based on user input.
        """
        try:
            self.duplicate_criteria = criteria
            record_action(f"Configured duplicate detection criteria: {criteria}")
        except Exception as e:
            error_message = f"Error configuring duplicate detection criteria: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def detect_and_eliminate_duplicates(self):
        """
        Detect and eliminate duplicates based on the configured criteria.
        """
        try:
            duplicates_info = detect_duplicates(self.consolidated_data, self.duplicate_criteria)
            if duplicates_info['duplicates_found']:
                record_action("Duplicates detected in the consolidated data.")
                # Eliminate duplicates
                self.consolidated_data = eliminate_duplicates(self.consolidated_data, duplicates_info['duplicate_indices'])
                record_action("Duplicates eliminated from the consolidated data.")
                log_event("Duplicates eliminated successfully.")
            else:
                record_action("No duplicates found in the consolidated data.")
                log_event("No duplicates to eliminate.")
        except Exception as e:
            error_message = f"Error detecting or eliminating duplicates: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def save_consolidated_dataset(self, output_path):
        """
        Save the consolidated dataset to the specified path.
        """
        try:
            save_consolidated_data(self.consolidated_data, output_path)
            record_action(f"Consolidated data saved to '{output_path}'")
            log_event("Consolidated data saved successfully.")
        except Exception as e:
            error_message = f"Error saving consolidated data: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e
