# modules/data_validation.py

import pandas as pd
from data_unificator.utils.validation_utils import (
    validate_completeness,
    validate_correctness,
    validate_consistency,
    flag_missing_data,
    ensure_foreign_keys,
    ensure_logical_consistency,
    check_time_series_consistency,
    verify_metadata,
    recalculate_derived_fields,
    check_impossible_values,
    remove_duplicate_records,
    ensure_data_formats,
    ensure_string_patterns,
    verify_audit_trails,
    perform_statistical_analysis,
    apply_business_rules,
)
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action
import traceback

class DataValidator:
    def __init__(self, consolidated_data):
        """
        Initialize the DataValidator with the consolidated dataset.
        """
        self.consolidated_data = consolidated_data  # Pandas DataFrame
        self.validation_results = {}
        self.user_actions = {}

    def perform_validation(self):
        """
        Perform all validation checks on the dataset.
        """
        try:
            # Completeness
            completeness_issues = validate_completeness(self.consolidated_data)
            self.validation_results['completeness'] = completeness_issues
            record_action("Performed completeness validation.")

            # Correctness
            correctness_issues = validate_correctness(self.consolidated_data)
            self.validation_results['correctness'] = correctness_issues
            record_action("Performed correctness validation.")

            # Consistency
            consistency_issues = validate_consistency(self.consolidated_data)
            self.validation_results['consistency'] = consistency_issues
            record_action("Performed consistency validation.")

            # Flag Missing Data
            missing_data = flag_missing_data(self.consolidated_data)
            self.validation_results['missing_data'] = missing_data
            record_action("Flagged missing data.")

            # Ensure Foreign Keys
            foreign_key_issues = ensure_foreign_keys(self.consolidated_data)
            self.validation_results['foreign_keys'] = foreign_key_issues
            record_action("Checked foreign key relationships.")

            # Logical Consistency
            logical_issues = ensure_logical_consistency(self.consolidated_data)
            self.validation_results['logical_consistency'] = logical_issues
            record_action("Ensured logical consistency.")

            # Time-Series Consistency
            time_series_issues = check_time_series_consistency(self.consolidated_data)
            self.validation_results['time_series'] = time_series_issues
            record_action("Checked time-series consistency.")

            # Metadata Verification
            metadata_issues = verify_metadata(self.consolidated_data)
            self.validation_results['metadata'] = metadata_issues
            record_action("Verified metadata consistency.")

            # Recalculate Derived Fields
            derived_field_issues = recalculate_derived_fields(self.consolidated_data)
            self.validation_results['derived_fields'] = derived_field_issues
            record_action("Recalculated derived fields.")

            # Impossible Values
            impossible_values = check_impossible_values(self.consolidated_data)
            self.validation_results['impossible_values'] = impossible_values
            record_action("Checked for impossible values.")

            # Remove Duplicate Records
            duplicates_removed = remove_duplicate_records(self.consolidated_data)
            if duplicates_removed:
                record_action("Removed duplicate records.")

            # Ensure Data Formats
            format_issues = ensure_data_formats(self.consolidated_data)
            self.validation_results['data_formats'] = format_issues
            record_action("Ensured data formats are consistent.")

            # Ensure String Patterns
            string_pattern_issues = ensure_string_patterns(self.consolidated_data)
            self.validation_results['string_patterns'] = string_pattern_issues
            record_action("Ensured string patterns are valid.")

            # Verify Audit Trails
            audit_issues = verify_audit_trails()
            self.validation_results['audit_trails'] = audit_issues
            record_action("Verified audit trails.")

            # Statistical Analysis
            anomalies = perform_statistical_analysis(self.consolidated_data)
            self.validation_results['statistical_anomalies'] = anomalies
            record_action("Performed statistical analysis.")

            # Apply Business Rules
            business_rule_issues = apply_business_rules(self.consolidated_data)
            self.validation_results['business_rules'] = business_rule_issues
            record_action("Applied business rules for validation.")

            log_event("Data validation completed successfully.")
        except Exception as e:
            error_message = f"Error during data validation: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            raise e
