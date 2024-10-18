# modules/data_mapping.py

import pandas as pd
import logging
import os
from datetime import datetime
from data_unificator.utils.mapping_utils import (
    extract_fields_metadata,
    identify_overlaps,
    rename_fields_in_data_structure,
    convert_field_types_in_data_structure,
    detect_conflicts,
    resolve_conflicts_in_dataframe,
    save_mapping_dictionary,
    load_mapping_dictionary,
    version_mapping_dictionary,
    verify_data_types,
    convert_data_types,
    check_non_ascii_characters,
    fix_non_ascii_characters,
    backup_file,
)
from data_unificator.utils.logging_utils import log_event, log_error
from data_unificator.audits.audit_trail import record_action
import traceback

class DataMapper:
    def __init__(self, data_sources):
        """
        Initialize the DataMapper with the imported data sources.
        """
        self.data_sources = data_sources  # List of dictionaries with keys: 'file', 'data', etc.
        self.field_metadata = {}
        self.modified_field_names = {}
        self.modified_field_types = {}
        self.mapping_dictionary = {}
        self.overlaps = []
        self.confirmed_overlaps = []
        self.conflicts = {}
        self.resolution_strategies = {}
        self.source_hierarchy = []
        self.mapping_version = 1
        self.load_existing_mappings()

    def load_existing_mappings(self):
        """
        Load existing mapping dictionary if available.
        """
        try:
            self.mapping_dictionary = load_mapping_dictionary()
            self.mapping_version = version_mapping_dictionary()
            record_action("Loaded existing mapping dictionary.")
        except FileNotFoundError:
            log_event("No existing mapping dictionary found.")
            self.mapping_dictionary = {}
            self.mapping_version = 1

    def extract_fields(self):
        """
        Extract fields and metadata from each data source.
        """
        try:
            for source in self.data_sources:
                data = source['data']
                file_name = source['file']
                file_path = source['file_path']
                hierarchy = source.get('hierarchy', None)

                # Fix Non-ASCII issues
            if isinstance(data, pd.DataFrame):
                non_ascii_issues = check_non_ascii_characters(data)
                if non_ascii_issues:
                    record_action(f"Non-ASCII characters found in '{file_name}': {non_ascii_issues}")
                    # Backup original file
                    backup_path = backup_file(file_path)
                    record_action(f"Backed up '{file_path}' to '{backup_path}'")
                    # Fix issues
                    data = fix_non_ascii_characters(data)
                    # Save fixed file
                    data.to_csv(file_path, index=False)
                    record_action(f"Fixed Non-ASCII issues in '{file_path}' and saved changes.")
                    source['data'] = data  # Update the data in the data_sources
                else:
                    # Handle non-DataFrame data structures
                    pass  # Implement if needed

                metadata = extract_fields_metadata(data)
                self.field_metadata[file_name] = {
                    'metadata': metadata,
                    'hierarchy': hierarchy
                }
                record_action(f"Extracted fields and metadata for '{file_name}'")
        except Exception as e:
            error_message = f"Error extracting fields: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def identify_overlapping_fields(self):
        """
        Identify overlapping fields based on shared field names across sources.
        """
        try:
            overlaps = identify_overlaps(self.field_metadata)
            self.overlaps = overlaps
            record_action("Identified overlapping fields.")
            return overlaps
        except Exception as e:
            error_message = f"Error identifying overlapping fields: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def align_structures(self):
        """
        Align data structures and hierarchies across sources using the mapping dictionary.
        """
        try:
            aligned_data = []
            for source in self.data_sources:
                df = source['data']
                file_name = source['file']
                #file_path = source['file_path']

                # Build reverse mapping for this source
                reverse_mapping = {}
                for standard_name, mappings in self.mapping_dictionary.items():
                    for src_name, field_name in mappings:
                        if src_name == file_name:
                            reverse_mapping[field_name] = standard_name

                # Apply modified field names
                if self.modified_field_names and file_name in self.modified_field_names:
                    field_name_mapping = self.modified_field_names[file_name]
                    if isinstance(df, pd.DataFrame):
                        df = df.rename(columns=field_name_mapping)
                    else:
                        df = rename_fields_in_data_structure(df, field_name_mapping)

                # Apply modified field types
                if self.modified_field_types and file_name in self.modified_field_types:
                    field_type_mapping = self.modified_field_types[file_name]
                    if isinstance(df, pd.DataFrame):
                        for field, new_type in field_type_mapping.items():
                            try:
                                df[field] = df[field].astype(new_type)
                            except Exception as e:
                                log_error(f"Convert field '{field}' to '{new_type}' in '{file_name}': {str(e)}")
                    else:
                        df = convert_field_types_in_data_structure(df, field_type_mapping)

                # Rename fields based on mapping
                if isinstance(df, pd.DataFrame):
                    df_renamed = df.rename(columns=reverse_mapping)
                else:
                    df_renamed = rename_fields_in_data_structure(df, reverse_mapping)

                aligned_data.append({'file': source['file'], 'data': df_renamed})
            self.aligned_data = aligned_data
            record_action("Aligned data structures across sources.")
        except Exception as e:
            error_message = f"Error aligning data structures: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def merge_data_sources(self):
        """
        Merge the source files in a bottom-up manner according to the source hierarchy.
        """
        try:
            # Start from the lowest priority source and merge upwards
            merged_data = None
            for source in reversed(self.source_hierarchy):
                df = None
                # Get the data from aligned_data (after applying mapping)
                for data_dict in self.aligned_data:
                    if data_dict['file'] == source:
                        df = data_dict['data']
                        break
                if df is None:
                    raise Exception(f"Data for source '{source}' not found in aligned data.")
                if merged_data is None:
                    merged_data = df
                else:
                    # Merge current df with merged_data using the anchor fields as keys
                    common_fields = list(set(merged_data.columns).intersection(set(df.columns)))
                    if not common_fields:
                        raise Exception(f"No common fields to merge between sources '{source}' and previous merged data.")
                    merged_data = pd.merge(merged_data, df, on=common_fields, how='outer')
            self.merged_data = merged_data
            record_action("Merged data sources into temporary merged data.")
        except Exception as e:
            error_message = f"Error merging data sources: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def save_temporary_merged_file(self, file_path):
        """
        Save the merged data to a temporary file.
        """
        try:
            self.merged_data.to_csv(file_path, index=False)
            record_action(f"Saved temporary merged file '{file_path}'.")
        except Exception as e:
            error_message = f"Error saving temporary merged file : {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def load_temporary_merged_file(self, file_path):
        """
        Load the temporary merged file.
        """
        try:
            self.merged_data = pd.read_csv(file_path)
            record_action(f"Loaded temporary merged file '{file_path}'.")
        except Exception as e:
            error_message = f"Error loading temporary merged file: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def get_conflicting_rows(self, conflict_key, field):
        """
        Get the conflicting rows for manual resolution.
        """
        keys = conflict_key if isinstance(conflict_key, tuple) else (conflict_key,)
        query_str = ' & '.join([f"`{col}` == {repr(val)}" for col, val in zip(self.merged_data.columns[:len(keys)], keys)])
        conflicting_rows = self.merged_data.query(query_str)
        return conflicting_rows[[field]]

    def mark_rows_for_deletion(self, conflict_key, field):
        """
        Mark conflicting rows for deletion.
        """
        keys = conflict_key if isinstance(conflict_key, tuple) else (conflict_key,)
        query_str = ' & '.join([f"`{col}` == {repr(val)}" for col, val in zip(self.merged_data.columns[:len(keys)], keys)])
        self.merged_data = self.merged_data.query(f"not ({query_str})")

    def update_conflict_value(self, conflict_key, field, new_value):
        """
        Update conflicting values with user-provided new value.
        """
        keys = conflict_key if isinstance(conflict_key, tuple) else (conflict_key,)
        condition = True
        for col, val in zip(self.merged_data.columns[:len(keys)], keys):
            condition = condition & (self.merged_data[col] == val)
        self.merged_data.loc[condition, field] = new_value

    def detect_conflicts(self, report_row_numbers=False):
        """
        Detect conflicts in data, formats, types, key pairs, and data structure.
        """
        try:
            conflicts = detect_conflicts([{'file': 'merged_data', 'data': self.merged_data}], report_row_numbers=report_row_numbers)
            self.conflicts = conflicts
            record_action("Detected conflicts in data.")
        except Exception as e:
            error_message = f"Error detecting conflicts: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def resolve_conflicts(self, strategy):
        """
        Resolve conflicts using the selected strategy.
        """
        if strategy == "Manual":
            # Assume that manual edits have been made to self.merged_data
            self.resolved_data = self.merged_data
        else:
            # Use existing conflict resolution methods
            self.detect_conflicts(report_row_numbers=False)
            self.resolved_data = resolve_conflicts_in_dataframe(self.merged_data, self.conflicts, strategy, self.source_weights, self.source_hierarchy)

    def save_resolved_data(self, file_path):
        """
        Save the resolved data to a file.
        """
        try:
            self.resolved_data.to_csv(file_path, index=False)
            record_action(f"Saved resolved data to '{file_path}'.")
        except Exception as e:
            error_message = f"Error saving resolved data to: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            raise e

    def verify_and_convert_data_types(self, user_conversions):
        """
        Verify data types and convert as per user selections.
        """
        try:
            incompatibilities = verify_data_types([{'data': self.resolved_data}])
            if incompatibilities:
                record_action(f"Data type incompatibilities found: {incompatibilities}")
                # Convert data types as per user input
                self.resolved_data = convert_data_types([{'data': self.resolved_data}], user_conversions)[0]['data']
                record_action("Converted data types based on user selections.")
            else:
                record_action("No data type incompatibilities found.")
        except Exception as e:
            error_message = f"Error verifying or converting data types: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def save_mapping(self):
        """
        Save the current mapping dictionary with versioning.
        """
        try:
            save_mapping_dictionary(self.mapping_dictionary, self.mapping_version)
            record_action(f"Saved mapping dictionary version {self.mapping_version}.")
            self.mapping_version += 1
        except Exception as e:
            error_message = f"Error saving mapping dictionary: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e
