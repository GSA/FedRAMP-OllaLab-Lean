# utils/normalization_utils.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from data_unificator.utils.logging_utils import log_error
from unidecode import unidecode

def standardize_formats(df):
    """
    Standardize data formats (dates, numbers, text casing).
    """
    # Convert date and time columns to datetime format
    for column in df.columns:
        if 'date' in column.lower() or 'time' in column.lower():
            try:
                df[column] = pd.to_datetime(df[column], errors='coerce')
            except Exception as e:
                log_error(f"Error converting column '{column}' to datetime: {str(e)}")
    # Standardize text casing to lowercase
    df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    return df

def handle_data_types(df):
    """
    Convert different data types into a unified format.
    """
    # Attempt to convert object columns to numeric
    for column in df.select_dtypes(include=['object']).columns:
        try:
            df[column] = pd.to_numeric(df[column], errors='ignore')
        except Exception as e:
            log_error(f"Error converting column '{column}' to numeric: {str(e)}")
    return df

def standardize_units(df):
    """
    Standardize units of measurement.
    """
    # Placeholder implementation
    # Actual unit conversion logic would go here
    return df

def detect_outliers(df_list):
    """
    Detect extreme outliers in numerical columns across multiple DataFrames.
    """
    outlier_info = []
    for data in df_list:
        df = data['data']
        outliers = {}
        for column in df.select_dtypes(include=[np.number]).columns:
            col_mean = df[column].mean()
            col_std = df[column].std()
            if col_std == 0:
                continue  # Avoid division by zero
            z_scores = (df[column] - col_mean) / col_std
            outlier_indices = df[np.abs(z_scores) > 3].index.tolist()
            if outlier_indices:
                outliers[column] = outlier_indices
        if outliers:
            outlier_info.append({'file': data['file'], 'outliers': outliers})
    return outlier_info if outlier_info else None

def apply_outlier_handling(df, outlier_info, action):
    """
    Apply selected action to handle outliers.
    """
    for column, indices in outlier_info.items():
        if action == "Capping":
            # Cap values at the threshold (mean ± 3*std)
            threshold_upper = df[column].mean() + 3 * df[column].std()
            threshold_lower = df[column].mean() - 3 * df[column].std()
            df.loc[df[column] > threshold_upper, column] = threshold_upper
            df.loc[df[column] < threshold_lower, column] = threshold_lower
        elif action == "Removal":
            # Remove rows containing outliers
            df.drop(index=indices, inplace=True)
        elif action == "Transformation":
            # Apply log transformation to positive values
            df[column] = df[column].apply(lambda x: np.log1p(x) if x > 0 else x)
        # Ignore action does nothing
    return df

def apply_scaling(df, scaling_options):
    """
    Apply scaling to selected fields.
    """
    fields = scaling_options.get('fields', [])
    method = scaling_options.get('method', '')
    if not fields or not method:
        return df  # No fields or method specified

    scaler = None
    if method == "Min-Max Scaling (0-1)":
        scaler = MinMaxScaler()
    elif method == "Z-score Normalization":
        scaler = StandardScaler()
    else:
        log_error(f"Unsupported scaling method: {method}")
        return df

    try:
        df[fields] = scaler.fit_transform(df[fields])
    except Exception as e:
        log_error(f"Error applying scaling to fields {fields}: {str(e)}")
    return df

def aggregate_fields(df, aggregation_options):
    """
    Aggregate new fields from existing fields.
    """
    for option in aggregation_options:
        new_field = option.get('new_field', '')
        fields = option.get('fields', [])
        operation = option.get('operation', '')
        if not new_field or not fields or not operation:
            continue  # Skip invalid aggregation option

        try:
            if operation == "Sum":
                df[new_field] = df[fields].sum(axis=1)
            elif operation == "Average":
                df[new_field] = df[fields].mean(axis=1)
            elif operation == "Max":
                df[new_field] = df[fields].max(axis=1)
            elif operation == "Min":
                df[new_field] = df[fields].min(axis=1)
            else:
                log_error(f"Unsupported aggregation operation: {operation}")
        except Exception as e:
            log_error(f"Error aggregating fields {fields} into {new_field}: {str(e)}")
    return df

def remove_fields(df, fields_to_remove):
    """
    Remove selected fields from the DataFrame.
    """
    try:
        df.drop(columns=fields_to_remove, inplace=True, errors='ignore')
    except Exception as e:
        log_error(f"Error removing fields {fields_to_remove}: {str(e)}")
    return df

def standardize_encoding(df):
    """
    Standardize text encoding to ASCII.
    """
    df = df.applymap(lambda x: unidecode(str(x)) if isinstance(x, str) else x)
    return df
