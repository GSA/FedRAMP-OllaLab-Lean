# modules/data_mapping.py

import pandas as pd
import logging
from data_unificator.utils.mapping_utils import (
    extract_fields_metadata,
    identify_overlaps,
    rename_fields_in_data_structure,
    convert_field_types_in_data_structure,
    detect_conflicts,
    resolve_conflicts,
    save_mapping_dictionary,
    load_mapping_dictionary,
    version_mapping_dictionary,
    verify_data_types,
    convert_data_types,
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
        self.source_weights = {}
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
                hierarchy = source.get('hierarchy', None)
                
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

    def detect_and_resolve_conflicts(self, user_selected_strategy):
        """
        Detect conflicts and resolve them based on user-selected strategy.
        """
        try:
            conflicts = detect_conflicts(self.aligned_data)
            self.conflicts = conflicts
            record_action("Detected conflicts in data.")
            # Resolve conflicts
            resolved_data = resolve_conflicts(
                self.aligned_data,
                conflicts,
                user_selected_strategy,
                self.source_weights,
                self.source_hierarchy
            )
            self.resolved_data = resolved_data
            record_action("Resolved conflicts using selected strategy.")
        except Exception as e:
            error_message = f"Error resolving conflicts: {str(e)}"
            log_error(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            record_action(error_message)
            raise e

    def verify_and_convert_data_types(self, user_conversions):
        """
        Verify data types and convert as per user selections.
        """
        try:
            incompatibilities = verify_data_types(self.resolved_data)
            if incompatibilities:
                record_action(f"Data type incompatibilities found: {incompatibilities}")
                # Convert data types as per user input
                self.resolved_data = convert_data_types(self.resolved_data, user_conversions)
                record_action("Converted data types based on user selections.")
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
