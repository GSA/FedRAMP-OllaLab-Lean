# modules/data_mapping.py

import pandas as pd
import logging
from data_unificator.utils.mapping_utils import (
    extract_fields_metadata,
    identify_overlaps,
    align_data_structures,
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

    def review_fields(self):
        """
        Review fields and metadata from each imported data source
        """
        try:
            for source in self.data_sources:
                data = source['data']
                file_name = source['file']
                file_extension = source['file_extension']
                hierarchy = source.get('hierarchy', None)
                
                metadata = extract_fields_metadata(data, file_extension, hierarchy)
                self.field_metadata[file_name] ={
                    'metadata': metadata,
                    'hierarchy': hierarchy
                }
                record_action(f"extract_field_metadata - {file_name}")
        except Exception as e:
            error_message = f"Error reviewing fields - {str(e)}"
            log_error(error_message)
            # add traceback logistics here later
    
    def update_field_names(self, file_name, field_name_mapping):
        """
        Update field names for a given file based on user input
        : param field_name_mapping: dictionary mapping original field names to new field names
        """
        self.modified_field_names[file_name] = field_name_mapping
        # doublecheck this
    
    def update_field_types (self, file_name, field_type_mapping):
        """
        Update field data types for a given file based on user input
        : param field_type_mapping: dictionary mapping field names to new data types
        """
        self.modified_field_types[file_name] = field_type_mapping

    def extract_fields(self):
        """
        Extract fields and metadata from each data source.
        """
        try:
            for source in self.data_sources:
                metadata = extract_fields_metadata(source['data'])
                self.field_metadata[source['file']] = metadata
                record_action(f"Extracted metadata from '{source['file']}'")
        except Exception as e:
            error_message = f"Error extracting fields: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            traceback_str = traceback.format_exc()
            log_error(traceback_str)
            raise e

    def identify_overlapping_fields(self):
        """
        Identify overlapping fields based on names.
        """
        try:
            overlaps = identify_overlaps(self.field_metadata)
            self.overlaps = overlaps
            record_action("Identified overlapping fields.")
            return overlaps
        except Exception as e:
            error_message = f"Error identifying overlapping fields: {str(e)}"
            log_error(error_message)
            record_action(error_message)
            raise e

    def align_structures(self):
        """
        Align data structures and hierarchies across sources.
        """
        try:
            self.aligned_data = align_data_structures(
                self.data_sources, 
                self.mapping_dictionary,
                self.modified_field_names,
                self.modified_field_types
            )
            record_action("Aligned data structures across sources.")
        except Exception as e:
            error_message = f"Error aligning data structures: {str(e)}"
            log_error(error_message)
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
                # Allow user to convert data types via GUI
                self.resolved_data = convert_data_types(self.resolved_data, user_conversions)
                record_action("Converted data types based on user selections.")
        except Exception as e:
            error_message = f"Error verifying or converting data types: {str(e)}"
            log_error(error_message)
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
            record_action(error_message)
            raise e
