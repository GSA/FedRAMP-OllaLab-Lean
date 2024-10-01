# utils/mapping_utils.py

import pandas as pd
from difflib import SequenceMatcher
import yaml
import os
from data_unificator.utils.logging_utils import log_error

def extract_fields_metadata(df):
    """
    Extract metadata for each field in the DataFrame.
    """
    metadata = {}
    for column in df.columns:
        metadata[column] = {
            'dtype': str(df[column].dtype),
            'sample_values': df[column].head(5).tolist(),
        }
    return metadata

def identify_overlaps(field_metadata):
    """
    Identify overlapping fields based on names using fuzzy matching.
    """
    overlaps = []
    all_fields = []
    for source, metadata in field_metadata.items():
        all_fields.extend(metadata.keys())

    unique_fields = list(set(all_fields))
    for i in range(len(unique_fields)):
        for j in range(i+1, len(unique_fields)):
            field1 = unique_fields[i]
            field2 = unique_fields[j]
            similarity = SequenceMatcher(None, field1, field2).ratio()
            if similarity > 0.8 and field1 != field2:
                overlaps.append({'fields': [field1, field2], 'similarity': similarity})
    return overlaps

def align_data_structures(data_sources, mapping_dictionary):
    """
    Align data structures based on the mapping dictionary.
    """
    aligned_data = []
    for source in data_sources:
        df = source['data']
        # Reverse the mapping dictionary to map original names to standard names
        reverse_mapping = {}
        for standard_name, original_names in mapping_dictionary.items():
            for original_name in original_names:
                reverse_mapping[original_name] = standard_name
        df_renamed = df.rename(columns=reverse_mapping)
        aligned_data.append({'file': source['file'], 'data': df_renamed})
    return aligned_data

def detect_conflicts(aligned_data):
    """
    Detect conflicts in data, formats, types, key pairs, and data structure.
    """
    conflicts = {}
    # Implement conflict detection logic
    # Placeholder example: conflicting values for the same key
    return conflicts

def resolve_conflicts(aligned_data, conflicts, strategy, source_weights, source_hierarchy):
    """
    Resolve conflicts based on selected strategy.
    """
    resolved_data = aligned_data  # Placeholder
    # Implement conflict resolution based on strategy
    return resolved_data

def verify_data_types(resolved_data):
    """
    Verify that fields mapped together have compatible data types.
    """
    incompatibilities = {}
    # Collect data types for each field across all data sources
    field_types = {}
    for data in resolved_data:
        df = data['data']
        for column in df.columns:
            dtype = str(df[column].dtype)
            if column not in field_types:
                field_types[column] = set()
            field_types[column].add(dtype)

    # Identify fields with incompatible data types
    for field, types in field_types.items():
        if len(types) > 1:
            incompatibilities[field] = list(types)
    return incompatibilities

def convert_data_types(resolved_data, user_conversions):
    """
    Convert data types of selected fields as per user input.
    """
    for data in resolved_data:
        df = data['data']
        for field, new_type in user_conversions.items():
            try:
                df[field] = df[field].astype(new_type)
            except Exception as e:
                log_error(f"Error converting field '{field}' to '{new_type}': {str(e)}")
    return resolved_data

def save_mapping_dictionary(mapping_dictionary, version):
    """
    Save mapping dictionary to a YAML file with versioning.
    """
    file_name = f"mapping_dictionary_v{version}.yaml"
    os.makedirs('mappings', exist_ok=True)
    with open(os.path.join('mappings', file_name), 'w') as f:
        yaml.dump(mapping_dictionary, f)

def load_mapping_dictionary():
    """
    Load the latest mapping dictionary.
    """
    mapping_files = [f for f in os.listdir('mappings') if f.startswith('mapping_dictionary')]
    if not mapping_files:
        raise FileNotFoundError("No mapping dictionary found.")
    latest_file = sorted(mapping_files)[-1]
    with open(os.path.join('mappings', latest_file), 'r') as f:
        mapping_dictionary = yaml.safe_load(f)
    return mapping_dictionary

def version_mapping_dictionary():
    """
    Get the next version number for the mapping dictionary.
    """
    mapping_files = [f for f in os.listdir('mappings') if f.startswith('mapping_dictionary')]
    if not mapping_files:
        return 1
    latest_file = sorted(mapping_files)[-1]
    version = int(latest_file.strip('mapping_dictionary_v').strip('.yaml'))
    return version + 1
