# utils/mapping_utils.py

import pandas as pd
from difflib import SequenceMatcher
import yaml
import os
from data_unificator.utils.logging_utils import log_error

def extract_fields_metadata(df):
    """
    Extract metadata for each field in the imported data.
    Handles both tabular (data frame) and non-tabular (JSON, XML)
    """
    metadata = {}
    if isinstance(data, pd.DataFrame):
        for column in data.columns:
            metadata[column] = {
                'dtype': str(data[column].dtype),
                'sample_values': df[column].head(2).tolist(),
            }
    else:
        # handle non-tabular
        def traverse (data, path=""):
            if isinstance (data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict,list)):
                        traverse(value, current_path)
                    else:
                        dtype = type(value).__name__
                        sample_values = [value]
                        if current_path not in metadata:
                            metadata[current_path] = {
                                'dtype': dtype,
                                'sample_values': sample_values,
                            }
                        else:
                            metadata[current_path]['sample_values'].append(value)
            elif isinstance (data, list):
                for index, item in enumerate(date):
                    traverse(item, path)
            else:
                pass # leaf node
        traverse (data)
    return metadata

def identify_overlaps(field_metadata):
    """
    Identify overlapping fields based on names using fuzzy matching.
    """
    overlaps = []
    all_fields = []
    field_sources = {}
    for source, meta in field_metadata.items():
        fields = meta['metadata'].keys()
        for field in fields:
            all_fields.append(field)
            if field not in field_sources:
                field_sources[field] = set()
            field_sources[field].add(source)

    unique_fields = list(set(all_fields))
    for i in range(len(unique_fields)):
        for j in range(i+1, len(unique_fields)):
            field1 = unique_fields[i]
            field2 = unique_fields[j]
            similarity = SequenceMatcher(None, field1, field2).ratio()
            if similarity > 0.8 and field1 != field2:
                overlaps.append({'fields': [field1, field2], 'similarity': similarity})
    return overlaps

def align_data_structures(data_sources, mapping_dictionary, modified_field_names=None, modified_field_types=None):
    """
    Align data structures based on the mapping dictionary.
    """
    aligned_data = [] # return this df regardless of data source is tabular or not
    for source in data_sources:
        df = source['data']
        file_name = source['file']
        file_extension = source['file_extension']
        # apply modified field names
        if modified_field_names and file_name in modified_field_names:
            field_name_mapping = modified_field_names[file_name]
            if isinstance (df, pd.DataFrame):
                df = df.rename(columns=field_name_mapping)
            else:
                df = rename_fields_in_data_structure(df, field_name_mapping) #doublecheck this
        # apply modified field types
        if modified_field_types and file_name in modified_field_types:
            field_type_mapping = modified_field_types[file_name]
            if isinstance(df, pd.DataFrame):
                for field, new_type in field_type_mapping.items():
                    try:
                        df[field] = df[field].astype(new_type)
                    except Exception as e:
                        log_error(f"Convert field - {field} to {new_type}") 
            else:
                df = convert_field_types_in_data_structure(df, field_type_mapping) #doublecheck this
        # reverse the mapping dictionary to map original names to standard names
        reverse_mapping = {}
        for standard_name, original_names in mapping_dictionary.items():
            for original_name in original_names:
                reverse_mapping[original_name] = standard_name
        if isinstance (df, pd.DataFrame):
            df_renamed = df.rename(columns=reverse_mapping)
        else:
            df_rename = rename_fields_in_data_structure(df, reverse_mapping)
        aligned_data.append({'file': source['file'], 'data': df_renamed})
    return aligned_data

def rename_fields_in_data_structure(data, field_name_mapping):
    """
    Rename fields in data structure (dict/list) based on field name mapping
    """
    if isinstance(data, dict):
        new_data = {}
        new_key = field_name_mapping.get(key, key)
        new_data[new_key] = rename_fields_in_data_structure(value, field_name_mapping)
        return new_data
    elif isinstance(data, list):
        return [rename_fields_in_data_structure(item, field_name_mapping) for item in data]
    else:
        return data

def convert_field_types_in_data_structure (data, field_type_mapping, path=""):
    """
    Convert field types in a data structure based on field type mapping
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if current_path in field_type_mapping:
                new_type = field_type_mapping[current_path]
                new_value = convert_value_to_type(value, new_type)
                new_data[key] = new_value
            else:
                new_data[key] = convert_field_types_in_data_structure (value, field_type_mapping, current_path)
            return new_data
    elif isinstance(data, list):
        return [convert_field_types_in_data_structure(item, field_type_mapping,path) for item in data]
    else:
        return data

def convert_value_to_type(value, new_type):
    try:
        if new_type == 'int':
            return int(value)
        elif new_type == 'float':
            return float(value)
        elif new_type == 'str':
            return str(value)
        elif new_type == 'datetime':
            from datetime import datetime
            return datetime.strptime(value, "%Y-%m-%d")
        else:
            return value
    except Exception as e:
        log_error(f"Data type convert - {value} to {new_type}" - {str(e)})
        return value # return original value if conversion fails

def detect_conflicts(aligned_data):
    """
    Detect conflicts in data, formats, types, key pairs, and data structure.
    aligned_data must be a data frame
    """
    conflicts = {}
    # collect all data into a list
    data_frames = []
    source_names = []
    for data_dict in aligned_data:
        df = data_dict['data']
        file_name = data_dict['file']
        if isinstance(df, pd.DataFrame):
            df_copy = df.copy()
            df_copy['source'] = file_name
            data_frames.append(df_copy)
            source_names.append(file_name)
        else:
            continue # this function only process DF
    
    # find common columns
    common_columns = set.intersection(*(set(df.columns) for df in data_frames))
    if not common_columns:
        # all data sources to be joined must share at least 1 column
        # need to improve this to support multi-levle joins
        return conflicts

    common_columns.discard('_source')
    key_columns = list(common_columns) # use common columns as keys
    if not key_columns:
        return conflicts

    # concatenate all data
    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    grouped = combined_df.groupby(key_columns)

    # detect conflicts in groups
    for group_keys, group in grouped:
        if len(group['_source']).unique()) > 1:
            conflicting_fields = {}
            for column in combined_df.columns:
                if column in key_columns or column == '_source':
                    continue
                values = group[column].dropna().unique()
                if len(values) >1:
                    conflicting_values={}
                    for source in source_names:
                        source_values = group[group['_source'] == source][column].dropna().unique()
                        if len(source_values) >0:
                            conflicting_values[source] = source_values.tolist()
                    conflicting_fields[column] = conflicting_values
            if conflicting_fields:
                conflicts[group_keys] = conflicting_fields
    return conflicts

def resolve_conflicts(aligned_data, conflicts, strategy, source_weights, source_hierarchy):
    """
    Resolve conflicts based on selected strategy.
    """
    if strategy == "Manual":
        return aligned_data # no implementation for this yet
    elif strategy == 'Hierarchy-based':
        resolved_data = resolve_conflicts_hierarchy(aligned_data, source_hierarchy)
    elif strategy == 'Weight-based':
        resolved_data = resolve_conflicts_weighted(aligned_data, source_hierarchy)
    elif strategy == 'Time-based':
        resolved_data = resolve_conflicts_time_based(aligned_data, source_hierarchy)
    else:
        resolved_data = aligned_data
    return resolved_data

def resolve_conflicts_hierarchy(aligned_data, source_hierarchy):
    return
def resolve_conflicts_weighted(aligned_data, source_hierarchy):
    return
def resolve_conflicts_time_based(aligned_data, source_hierarchy):
    return
    
def verify_data_types(resolved_data):
    """
    Verify that fields mapped together have compatible data types.
    """
    incompatibilities = {}
    # Collect data types for each field across all data sources
    field_types = {}
    for data in resolved_data:
        df = data['data']
        if isinstance (df, pd.DataFrame):
            for column in df.columns:
                dtype = str(df[column].dtype)
                if column not in field_types:
                    field_types[column] = set()
                field_types[column].add(dtype)
        else:
            collect_field_types_in_data_structure(df, field_types)
    # identify incompativle data types
    for field, types in field_types.items():
        if len(types) >1:
            incompatibilities[field] = list (types)
    return incompatibilities

def collect_field_types_in_data_structure (data, field_types, path=""):
    """
    Collect data types from data structures to check for incompatibilities
    """
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value,(dict, list)):
                collect_field_types_in_data_structure(value, field_types, current_path)
            else:
                dtype = type(value).__name__
                if current_path not in field_types:
                    field_types[current_path] = set()
                field_types[current_path].add(dtype)
    elif isinstance(data, list):
        for item in data:
            collect_field_types_in_data_structure(item, field_types, path)

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
        if isinstance (df, pd.DataFrame):
            for field, new_type in user_conversions.items():
                try:
                    df[field] = df[field].astype(new_type)
                except Exception as e:
                    log_error(f"Error converting field '{field}' to '{new_type}': {str(e)}")
        else:
            df = convert_field_types_in_data_structure(df, user_conversions)
        data['data'] = df
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
    mapping_files.sort(key=lambda x: int(x[len('mapping_dictionary_v'):-len('.yaml')]))
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
    mapping_files.sort(key=lambda x: int(x[len('mapping_dictionary_v'):-len('.yaml')]))
    latest_file = mapping_files[-1]
    version_str = latest_file[len('mapping_dictionary_v'):-len('.yaml')]
    version = int(version_str)
    return version + 1
