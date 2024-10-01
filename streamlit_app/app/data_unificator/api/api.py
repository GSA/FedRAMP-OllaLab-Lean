# api/api.py

import multiprocessing
from data_unificator.modules import (
    data_import,
    data_mapping,
    data_normalization,
    data_deduplication,
    data_validation,
)
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action

class DataUnificatorAPI:
    def __init__(self, num_workers=1):
        self.num_workers = num_workers

    def process_data_import(self, file_paths):
        """
        Process data import in parallel.
        """
        try:
            with multiprocessing.Pool(processes=self.num_workers) as pool:
                results = pool.map(data_import.import_single_file, file_paths)
            record_action(f"Data import completed for {len(file_paths)} files.")
            return results
        except Exception as e:
            error_message = f"Error in data import API: {str(e)}"
            log_error(error_message)
            raise e

    def process_data_mapping(self, data_sources, user_input):
        """
        Process data mapping.
        """
        try:
            data_mapper = data_mapping.DataMapper(data_sources)
            data_mapper.extract_fields()
            data_mapper.identify_overlapping_fields()
            data_mapper.source_hierarchy = user_input.get('source_hierarchy', [])
            data_mapper.source_weights = user_input.get('source_weights', {})
            data_mapper.align_structures()
            data_mapper.detect_and_resolve_conflicts(user_input.get('conflict_strategy'))
            data_mapper.save_mapping()
            record_action("Data mapping completed.")
            return data_mapper.resolved_data
        except Exception as e:
            error_message = f"Error in data mapping API: {str(e)}"
            log_error(error_message)
            raise e

    def process_data_normalization(self, resolved_data, user_input):
        """
        Process data normalization.
        """
        try:
            data_normalizer = data_normalization.DataNormalizer(resolved_data)
            data_normalizer.standardize_data_formats()
            data_normalizer.handle_data_types()
            data_normalizer.standardize_units_of_measurement()
            data_normalizer.detect_and_handle_outliers(user_input.get('outlier_actions'))
            data_normalizer.apply_scaling_to_fields(user_input.get('scaling_options'))
            data_normalizer.aggregate_and_remove_fields(
                user_input.get('aggregation_options'),
                user_input.get('fields_to_remove')
            )
            data_normalizer.standardize_text_encoding()
            record_action("Data normalization completed.")
            return data_normalizer.resolved_data
        except Exception as e:
            error_message = f"Error in data normalization API: {str(e)}"
            log_error(error_message)
            raise e

    def process_data_deduplication(self, normalized_data, user_input):
        """
        Process data deduplication.
        """
        try:
            data_deduplicator = data_deduplication.DataDeduplicator(normalized_data)
            data_deduplicator.merge_data()
            data_deduplicator.configure_duplicate_detection(user_input.get('duplicate_criteria'))
            data_deduplicator.detect_and_eliminate_duplicates()
            record_action("Data deduplication completed.")
            return data_deduplicator.consolidated_data
        except Exception as e:
            error_message = f"Error in data deduplication API: {str(e)}"
            log_error(error_message)
            raise e

    def process_data_validation(self, consolidated_data):
        """
        Process data validation.
        """
        try:
            data_validator = data_validation.DataValidator(consolidated_data)
            data_validator.perform_validation()
            record_action("Data validation completed.")
            return data_validator.validation_results
        except Exception as e:
            error_message = f"Error in data validation API: {str(e)}"
            log_error(error_message)
            raise e
