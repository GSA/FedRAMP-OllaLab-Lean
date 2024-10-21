# utils/mapping_utils.py

import pandas as pd
from difflib import SequenceMatcher
import yaml
import os
import re
from datetime import datetime
from data_unificator.utils.logging_utils import log_error

def extract_fields_metadata(data):
    """
    Extract metadata for each field in the imported data.
    Handles both tabular (DataFrame) and non-tabular (JSON, XML).
    """
    metadata = {}
    max_sample_values = 5  # Limit the number of sample values per field
    if isinstance(data, pd.DataFrame):
        for column in data.columns:
            metadata[column] = {
                'dtype': str(data[column].dtype),
                'sample_values': data[column].dropna().unique().tolist()[:max_sample_values],
            }
    else:
        # Handle non-tabular data structures
        def traverse(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        traverse(value, current_path)
                    else:
                        dtype = type(value).__name__
                        if current_path not in metadata:
                            metadata[current_path] = {
                                'dtype': dtype,
                                'sample_values': [value],
                            }
                        else:
                            if len(metadata[current_path]['sample_values']) < max_sample_values:
                                metadata[current_path]['sample_values'].append(value)
            elif isinstance(data, list):
                for item in data:
                    traverse(item, path)
            else:
                pass  # Leaf node

        traverse(data)
    return metadata

def identify_overlaps(field_metadata):
    """
    Identify overlapping fields based on shared field names across sources.
    For each shared field name, verify whether the data types and data value patterns are similar.
    """
    overlaps = []
    field_info = {}
    # Collect field info for each field name across sources
    for source, meta in field_metadata.items():
        fields = meta.get('metadata', {})
        for field_name, field_meta in fields.items():
            if field_name not in field_info:
                field_info[field_name] = {}
            field_info[field_name][source] = field_meta

    # Now, for each field name that exists in more than one source
    for field_name, sources in field_info.items():
        if len(sources) > 1:
            # Collect data types and sample values from all sources
            data_types = {}
            sample_values_dict = {}
            for source_name, field_meta in sources.items():
                dtype = field_meta.get('dtype', 'N/A')
                sample_values = field_meta.get('sample_values', [])
                data_types[source_name] = dtype
                sample_values_dict[source_name] = sample_values

            # Check if data types are the same
            same_dtype = len(set(data_types.values())) == 1

            # Compute sample value similarities
            sample_similarity = {}
            source_names = list(sample_values_dict.keys())
            for i in range(len(source_names)):
                for j in range(i+1, len(source_names)):
                    source_a = source_names[i]
                    source_b = source_names[j]
                    values_a = sample_values_dict[source_a]
                    values_b = sample_values_dict[source_b]
                    similarity = compute_sample_similarity(values_a, values_b)
                    sample_similarity[(source_a, source_b)] = similarity

            overlaps.append({
                'field_name': field_name,
                'sources': list(sources.keys()),
                'data_types': data_types,
                'sample_values': sample_values_dict,
                'same_dtype': same_dtype,
                'sample_similarity': sample_similarity
            })
    return overlaps

def compute_sample_similarity(values_a, values_b):
    """
    Compute a similarity score between two lists of sample values.
    """
    set_a = set(values_a)
    set_b = set(values_b)
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0
    similarity = len(intersection) / len(union)
    return similarity

def check_non_ascii_characters(df):
    """
    Check for Non-ASCII characters in DataFrame, allowing specific characters.
    """
    allowed_chars = r'()[\]._-:'
    non_ascii_issues = {}
    pattern = re.compile(rf'[^\x00-\x7F{re.escape(allowed_chars)}]+')
    for column in df.columns:
        issues = df[df[column].astype(str).str.contains(pattern, na=False)]
        if not issues.empty:
            non_ascii_issues[column] = issues.index.tolist()
    return non_ascii_issues

def fix_non_ascii_characters(df):
    """
    Fix Non-ASCII characters in DataFrame, replacing them with a placeholder.
    """
    allowed_chars = r'()[\]._-:'
    pattern = re.compile(rf'[^\x00-\x7F{re.escape(allowed_chars)}]+')
    for column in df.columns:
        df[column] = df[column].astype(str).apply(lambda x: re.sub(pattern, '', x) if x else x)
    return df

def backup_file(file_path):
    """
    Backup the file with date and time appended to the filename.
    """
    try:
        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(directory, backup_filename)
        os.makedirs(directory, exist_ok=True)
        with open(file_path, 'rb') as original_file, open(backup_path, 'wb') as backup_file:
            backup_file.write(original_file.read())
        return backup_path
    except Exception as e:
        log_error(f"Error backing up file '{file_path}': {str(e)}")
        return None

def rename_fields_in_data_structure(data, field_name_mapping):
    """
    Rename fields in data structure (dict/list) based on field name mapping.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = field_name_mapping.get(key, key)
            new_data[new_key] = rename_fields_in_data_structure(value, field_name_mapping)
        return new_data
    elif isinstance(data, list):
        return [rename_fields_in_data_structure(item, field_name_mapping) for item in data]
    else:
        return data

def convert_field_types_in_data_structure(data, field_type_mapping, path=""):
    """
    Convert field types in a data structure based on field type mapping.
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
                new_data[key] = convert_field_types_in_data_structure(value, field_type_mapping, current_path)
        return new_data
    elif isinstance(data, list):
        return [convert_field_types_in_data_structure(item, field_type_mapping, path) for item in data]
    else:
        return data

def convert_value_to_type(value, new_type):
    """
    Convert a single value to the specified type.
    """
    try:
        if new_type == 'int':
            return int(value)
        elif new_type == 'float':
            return float(value)
        elif new_type == 'str':
            return str(value)
        elif new_type == 'datetime':
            return datetime.strptime(value, "%Y-%m-%d")
        else:
            return value
    except Exception as e:
        log_error(f"Data type conversion error: Unable to convert '{value}' to '{new_type}': {str(e)}")
        return value  # Return original value if conversion fails

def detect_conflicts(aligned_data, report_row_numbers=False):
    """
    Detect conflicts in data, formats, types, key pairs, and data structure.
    """
    conflicts = {}
    data_frames = []
    source_names = []
    for data_dict in aligned_data:
        df = data_dict.get('data')
        file_name = data_dict.get('file')
        if isinstance(df, pd.DataFrame):
            df_copy = df.copy()
            df_copy['_source'] = file_name
            data_frames.append(df_copy)
            source_names.append(file_name)
        else:
            continue  # Skip non-DataFrame data

    # Find common columns
    if not data_frames:
        return conflicts
    common_columns = set.intersection(*(set(df.columns) for df in data_frames))
    common_columns.discard('_source')
    key_columns = list(common_columns)

    if not key_columns:
        return conflicts

    # Concatenate all data
    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    grouped = combined_df.groupby(key_columns)

    # Detect conflicts in groups
    for group_keys, group in grouped:
        if len(group['_source'].unique()) > 1:
            conflicting_fields = {}
            for column in combined_df.columns:
                if column in key_columns or column == '_source':
                    continue
                values = group[column].dropna().unique()
                if len(values) > 1:
                    conflicting_values = {}
                    for source in source_names:
                        source_group = group[group['_source'] == source]
                        source_values = source_group[column].dropna().unique()
                        if len(source_values) > 0:
                            if report_row_numbers:
                                row_numbers = source_group.index.tolist()
                                conflicting_values[source] = {
                                    'values': source_values.tolist(),
                                    'rows': row_numbers
                                }
                            else:
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
        return aligned_data  # No implementation for manual resolution
    elif strategy == 'Hierarchy-based':
        resolved_data = resolve_conflicts_hierarchy(aligned_data, source_hierarchy)
    elif strategy == 'Time-based':
        resolved_data = resolve_conflicts_time_based(aligned_data)
    elif strategy == 'Weight-based':
        resolved_data = resolve_conflicts_weighted(aligned_data, source_weights)
    else:
        resolved_data = aligned_data
    return resolved_data

def resolve_conflicts_hierarchy(aligned_data, source_hierarchy):
    """
    Resolve conflicts based on source hierarchy.
    The source higher in the hierarchy has precedence.
    """
    source_priority = {source: idx for idx, source in enumerate(source_hierarchy)}
    data_frames = []
    for data_dict in aligned_data:
        df = data_dict.get('data')
        file_name = data_dict.get('file')
        if isinstance(df, pd.DataFrame):
            df_copy = df.copy()
            df_copy['_source'] = file_name
            df_copy['_priority'] = source_priority.get(file_name, len(source_priority))
            data_frames.append(df_copy)
        else:
            continue

    if not data_frames:
        return aligned_data

    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    common_columns = set.intersection(*(set(df.columns) for df in data_frames))
    common_columns.discard('_source')
    common_columns.discard('_priority')
    key_columns = list(common_columns)

    if not key_columns:
        return aligned_data

    combined_df = combined_df.sort_values('_priority')
    resolved_df = combined_df.drop_duplicates(subset=key_columns, keep='first')
    resolved_df = resolved_df.drop(columns=['_source', '_priority'])
    resolved_data = [{'file': 'resolved_data', 'data': resolved_df}]
    return resolved_data

def resolve_conflicts_weighted(aligned_data, source_weights):
    """
    Resolve conflicts based on source weights.
    The source with higher weight has precedence.
    """
    data_frames = []
    for data_dict in aligned_data:
        df = data_dict.get('data')
        file_name = data_dict.get('file')
        weight = source_weights.get(file_name, 0)
        if isinstance(df, pd.DataFrame):
            df_copy = df.copy()
            df_copy['_source'] = file_name
            df_copy['_weight'] = weight
            data_frames.append(df_copy)
        else:
            continue

    if not data_frames:
        return aligned_data

    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    common_columns = set.intersection(*(set(df.columns) for df in data_frames))
    common_columns.discard('_source')
    common_columns.discard('_weight')
    key_columns = list(common_columns)

    if not key_columns:
        return aligned_data

    combined_df = combined_df.sort_values('_weight', ascending=False)
    resolved_df = combined_df.drop_duplicates(subset=key_columns, keep='first')
    resolved_df = resolved_df.drop(columns=['_source', '_weight'])
    resolved_data = [{'file': 'resolved_data', 'data': resolved_df}]
    return resolved_data

def resolve_conflicts_time_based(aligned_data):
    """
    Resolve conflicts based on the latest timestamp.
    Assumes there is a 'timestamp' field in the data.
    """
    data_frames = []
    for data_dict in aligned_data:
        df = data_dict.get('data')
        file_name = data_dict.get('file')
        if isinstance(df, pd.DataFrame) and 'timestamp' in df.columns:
            df_copy = df.copy()
            df_copy['_source'] = file_name
            data_frames.append(df_copy)
        else:
            continue

    if not data_frames:
        return aligned_data

    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'], errors='coerce')
    combined_df = combined_df.dropna(subset=['timestamp'])

    common_columns = set.intersection(*(set(df.columns) for df in data_frames))
    common_columns.discard('_source')
    common_columns.discard('timestamp')
    key_columns = list(common_columns)

    if not key_columns:
        return aligned_data

    combined_df = combined_df.sort_values('timestamp', ascending=False)
    resolved_df = combined_df.drop_duplicates(subset=key_columns, keep='first')
    resolved_df = resolved_df.drop(columns=['_source', 'timestamp'])
    resolved_data = [{'file': 'resolved_data', 'data': resolved_df}]
    return resolved_data

def verify_data_types(resolved_data):
    """
    Verify that fields mapped together have compatible data types.
    """
    incompatibilities = {}
    field_types = {}
    for data in resolved_data:
        df = data.get('data')
        if isinstance(df, pd.DataFrame):
            for column in df.columns:
                dtype = str(df[column].dtype)
                if column not in field_types:
                    field_types[column] = set()
                field_types[column].add(dtype)
        else:
            collect_field_types_in_data_structure(df, field_types)

    for field, types in field_types.items():
        if len(types) > 1:
            incompatibilities[field] = list(types)
    return incompatibilities

def collect_field_types_in_data_structure(data, field_types, path=""):
    """
    Collect data types from data structures to check for incompatibilities.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                collect_field_types_in_data_structure(value, field_types, current_path)
            else:
                dtype = type(value).__name__
                if current_path not in field_types:
                    field_types[current_path] = set()
                field_types[current_path].add(dtype)
    elif isinstance(data, list):
        for item in data:
            collect_field_types_in_data_structure(item, field_types, path)

def convert_data_types(resolved_data, user_conversions):
    """
    Convert data types of selected fields as per user input.
    """
    for data in resolved_data:
        df = data.get('data')
        if isinstance(df, pd.DataFrame):
            for field, new_type in user_conversions.items():
                try:
                    if new_type == 'datetime':
                        df[field] = pd.to_datetime(df[field], errors='coerce')
                    else:
                        df[field] = df[field].astype(new_type)
                except Exception as e:
                    log_error(f"Error converting field '{field}' to '{new_type}': {str(e)}")
        else:
            df = convert_field_types_in_data_structure(df, user_conversions)
            data['data'] = df  # Update the data in the resolved_data
    return resolved_data

def save_mapping_dictionary(mapping_dictionary, version):
    """
    Save mapping dictionary to a YAML file with versioning.
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"mapping_dictionary_v{version}_{timestamp}.yaml"
        os.makedirs('mappings', exist_ok=True)
        with open(os.path.join('mappings', file_name), 'w') as f:
            yaml.dump(mapping_dictionary, f)
    except Exception as e:
        log_error(f"Error saving mapping dictionary: {str(e)}")

def load_mapping_dictionary():
    """
    Load the latest mapping dictionary.
    """
    try:
        mapping_dir = 'mappings'
        if not os.path.exists(mapping_dir):
            raise FileNotFoundError("Mapping directory does not exist.")

        mapping_files = [
            f for f in os.listdir(mapping_dir)
            if f.startswith('mapping_dictionary_v') and f.endswith('.yaml')
        ]
        if not mapping_files:
            raise FileNotFoundError("No mapping dictionary found.")

        # Sort files by modification time
        mapping_files.sort(key=lambda x: os.path.getmtime(os.path.join(mapping_dir, x)))
        latest_file = mapping_files[-1]
        with open(os.path.join(mapping_dir, latest_file), 'r') as f:
            mapping_dictionary = yaml.safe_load(f)
        return mapping_dictionary
    except Exception as e:
        log_error(f"Error loading mapping dictionary: {str(e)}")
        raise e

def version_mapping_dictionary():
    """
    Get the next version number for the mapping dictionary.
    """
    mapping_dir = 'mappings'
    if not os.path.exists(mapping_dir):
        return 1

    mapping_files = [
        f for f in os.listdir(mapping_dir)
        if f.startswith('mapping_dictionary_v') and f.endswith('.yaml')
    ]
    if not mapping_files:
        return 1

    versions = []
    for file in mapping_files:
        version_part = file[len('mapping_dictionary_v'):]
        version_str = version_part.split('_')[0]
        try:
            versions.append(int(version_str))
        except ValueError:
            continue  # Skip files that don't follow the naming convention

    if not versions:
        return 1
    return max(versions) + 1

def resolve_conflicts_in_dataframe(df, conflicts, strategy, source_weights, source_hierarchy):
    """
    Resolve conflicts in a DataFrame using the selected strategy.
    """
    if strategy == 'Hierarchy-based':
        resolved_df = resolve_conflicts_hierarchy_in_df(df, source_hierarchy)
    elif strategy == 'Time-based':
        resolved_df = resolve_conflicts_time_based_in_df(df)
    elif strategy == 'Weight-based':
        resolved_df = resolve_conflicts_weighted_in_df(df, source_weights)
    else:
        resolved_df = df  # For manual or unsupported strategies
    return resolved_df

def resolve_conflicts_hierarchy_in_df(df, source_hierarchy):
    """
    Implement conflict resolution in DataFrame based on hierarchy.
    The source higher in the hierarchy has precedence.
    """
    try:
        source_priority = {source: idx for idx, source in enumerate(source_hierarchy)}
        df['_priority'] = df['_source'].map(source_priority)
        df_sorted = df.sort_values('_priority')
        key_columns = [col for col in df.columns if col not in ['_source', '_priority']]
        resolved_df = df_sorted.drop_duplicates(subset=key_columns, keep='first')
        resolved_df = resolved_df.drop(columns=['_source', '_priority'])
        return resolved_df
    except Exception as e:
        log_error(f"Error in hierarchy-based conflict resolution: {str(e)}")
        return df

def resolve_conflicts_weighted_in_df(df, source_weights):
    """
    Implement conflict resolution in DataFrame based on weights.
    The source with higher weight has precedence.
    """
    try:
        df['_weight'] = df['_source'].map(source_weights)
        df_sorted = df.sort_values('_weight', ascending=False)
        key_columns = [col for col in df.columns if col not in ['_source', '_weight']]
        resolved_df = df_sorted.drop_duplicates(subset=key_columns, keep='first')
        resolved_df = resolved_df.drop(columns=['_source', '_weight'])
        return resolved_df
    except Exception as e:
        log_error(f"Error in weighted conflict resolution: {str(e)}")
        return df

def resolve_conflicts_time_based_in_df(df):
    """
    Implement conflict resolution in DataFrame based on time.
    Assumes there is a 'timestamp' field in the data.
    """
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df_sorted = df.sort_values('timestamp', ascending=False)
        key_columns = [col for col in df.columns if col not in ['_source', 'timestamp']]
        resolved_df = df_sorted.drop_duplicates(subset=key_columns, keep='first')
        resolved_df = resolved_df.drop(columns=['_source', 'timestamp'])
        return resolved_df
    except Exception as e:
        log_error(f"Error in time-based conflict resolution: {str(e)}")
        return df
