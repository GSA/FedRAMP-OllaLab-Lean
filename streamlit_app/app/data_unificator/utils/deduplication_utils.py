# utils/deduplication_utils.py

import pandas as pd
from rapidfuzz import fuzz
from data_unificator.utils.logging_utils import log_error
import os

def merge_datasets(dataframes):
    """
    Merge multiple DataFrames into a single DataFrame.
    """
    consolidated_df = pd.concat(dataframes, ignore_index=True)
    return consolidated_df

def list_common_fields(normalized_data):
    """
    List common fields across all datasets.
    """
    field_sets = [set(data['data'].columns) for data in normalized_data]
    common_fields = set.intersection(*field_sets)
    return list(common_fields)

def detect_duplicates(df, criteria_config):
    """
    Detect duplicates in the DataFrame based on selected criteria.
    """
    duplicates_info = {'duplicates_found': False, 'duplicate_indices': []}

    if not criteria_config['selected_criteria']:
        return duplicates_info  # No criteria selected

    try:
        if "Exact Match" in criteria_config['selected_criteria']:
            duplicate_indices = df[df.duplicated()].index.tolist()
            duplicates_info['duplicate_indices'].extend(duplicate_indices)

        if "Fuzzy Match" in criteria_config['selected_criteria']:
            threshold = criteria_config['similarity_threshold'] or 0.8
            # Placeholder implementation for fuzzy matching
            for i in range(len(df)):
                for j in range(i+1, len(df)):
                    row_i = df.iloc[i].astype(str).str.cat(sep=' ')
                    row_j = df.iloc[j].astype(str).str.cat(sep=' ')
                    similarity = fuzz.token_set_ratio(row_i, row_j) / 100
                    if similarity >= threshold:
                        duplicates_info['duplicate_indices'].append(j)

        if "Composite Key Matching" in criteria_config['selected_criteria']:
            fields = criteria_config['user_defined_fields']
            duplicate_indices = df[df.duplicated(subset=fields)].index.tolist()
            duplicates_info['duplicate_indices'].extend(duplicate_indices)

        if "Custom Rules" in criteria_config['selected_criteria']:
            # Implement custom rules as per domain-specific requirements
            pass

        duplicates_info['duplicates_found'] = bool(duplicates_info['duplicate_indices'])
        duplicates_info['duplicate_indices'] = list(set(duplicates_info['duplicate_indices']))
        return duplicates_info

    except Exception as e:
        log_error(f"Error detecting duplicates: {str(e)}")
        raise e

def eliminate_duplicates(df, duplicate_indices):
    """
    Eliminate duplicates from the DataFrame based on indices.
    """
    df_deduplicated = df.drop(index=duplicate_indices).reset_index(drop=True)
    return df_deduplicated

def save_consolidated_data(df, output_path):
    """
    Save the consolidated DataFrame to the specified output path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
