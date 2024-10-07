# modules/data_import.py

import os
import pandas as pd
import logging
import re
from multiprocessing import Pool
from data_unificator.utils.file_utils import (
    get_supported_files,
    read_file,
    detect_encoding,
    remove_duplicates_in_df,
    check_for_pii,
    save_file,
    backup_file
)
from data_unificator.utils.logging_utils import log_error, log_event
from data_unificator.utils.security_utils import sanitize_data
from data_unificator.utils.data_utils import perform_eda, extract_hierarchy, visualize_hierarchy
from data_unificator.audits.audit_trail import record_action
import traceback

def import_files_parallel(file_paths, num_workers):
    """
    Import files in parallel using multiprocessing.
    """
    with Pool(processes=num_workers) as pool:
        results = pool.map(import_single_file, file_paths)
    return results

def import_single_file(file_path):
    """
    Import a single file and perform necessary preprocessing.
    """
    skipped_entries = 0  # Track skipped entries
    base_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    try:
        # Detect encoding
        encoding = detect_encoding(file_path)
        record_action(f"Detected encoding '{encoding}' for file '{file_path}'")

        # Read the file
        df, skipped = read_file(file_path, encoding)
        skipped_entries += skipped
        if df is None or df.empty:
            error_message = f"File read error - '{file_path}'"
            log_error(error_message)
            record_action(error_message)
            return {
                "status": "error",
                "file": file_name,
                "error": error_message,
                "file_path": file_path,
                "skipped_entries": skipped_entries
            }

        # Sanitize cell data
        df = df.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)
        # Sanitize column names
        df.columns = [str(col) for col in df.columns]

        # Sanitize data to prevent issues like memory overflow
        df = sanitize_data(df)

        # Remove duplicates
        df = remove_duplicates_in_df(df)

        # Check for discrepancies
        discrepancies = find_discrepancies(df)

        # Check for missing data and show missing value counts per field
        missing_data_info = None
        if df.isnull().values.any():
            missing_data_info = df.isnull().sum()
            missing_data_info = missing_data_info[missing_data_info > 0]
            record_action(f"Missing data found in file '{file_path}': {missing_data_info.to_dict()}")

        # Check for PII
        pii_fields = check_for_pii(df)
        if pii_fields:
            record_action(f"PII data found in file '{file_path}': {pii_fields}")

        # If there are any issues, return with status 'issues_found'
        if discrepancies or (missing_data_info is not None and not missing_data_info.empty) or pii_fields:
            return {
                "status": "issues_found",
                "file": file_name,
                "file_path": file_path,
                "data": df,
                "discrepancies": discrepancies,
                "missing_data_info": missing_data_info,
                "pii_fields": pii_fields,
                "skipped_entries": skipped_entries
            }

        # No issues found, proceed to perform hierarchy extraction and EDA

        # Perform hierarchy extraction
        hierarchy = extract_hierarchy(df)
        hierarchy_path = os.path.join(
            base_path, f"{file_name.replace('.', '_')}_hierarchy.png"
        )
        visualize_hierarchy(hierarchy, save_path=hierarchy_path)

        # Perform EDA
        eda_report = perform_eda(df, file_path)
        record_action(f"EDA performed on file '{file_path}'")

        # Copy the file to the backup folder while keeping the original
        backup_folder = os.path.join(base_path, "backup")
        os.makedirs(backup_folder, exist_ok=True)
        backup_file(file_path, backup_folder)

        # Return success status along with hierarchy data
        return {
            "status": "success",
            "file": file_name,
            "file_path": file_path,
            "data": df,
            "eda_report": eda_report,
            "hierarchy_data": hierarchy,
            "skipped_entries": skipped_entries
        }

    except Exception as e:
        error_message = f"Error importing file '{file_path}': {str(e)}"
        log_error(error_message)
        record_action(error_message)
        traceback_str = traceback.format_exc()
        log_error(traceback_str)
        return {
            "status": "error",
            "file": file_name,
            "file_path": file_path,
            "error": error_message,
            "skipped_entries": skipped_entries
        }

# Fix functions
def fix_non_ascii_characters(df, column):
    from unidecode import unidecode
    df[column] = df[column].astype(str).apply(unidecode)
    return df

def fix_inconsistent_dates(df, column):
    """
    Standardize the date formats in the column.
    """
    from datetime import datetime

    # Define the target date format
    target_format = "%Y-%m-%d"

    # Function to parse and reformat dates
    def parse_and_format(date_str):
        for fmt in known_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(target_format)
            except ValueError:
                continue
        return date_str  # Return original if no format matches

    known_formats = [
        # Include all formats from infer_date_format
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
        # Add more formats as needed
    ]

    df[column] = df[column].dropna().apply(parse_and_format)
    return df


def fix_negative_values(df, column):
    df = df[df[column] >= 0]
    return df

def apply_data_fixes(file_path, missing_data_strategies=None, manual_inputs=None, pii_actions=None, discrepancies=None):
    """
    Apply the selected data fixes to the file, including missing data, PII, and discrepancies.
    """
    try:
        # Backup the original file before applying data fixes
        backup_folder = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_folder, exist_ok=True)
        backup_file(file_path, backup_folder)

        # Read the file into a DataFrame
        df, skipped_entries = read_file(file_path)
        if df is None or df.empty:
            error_message = f"File error - {file_path}"
            log_error(error_message)
            record_action(error_message)
            return False, None

        # Fix missing data
        if missing_data_strategies:
            for field, strategy in missing_data_strategies.items():
                if strategy == "Statistical Imputation":
                    if pd.api.types.is_numeric_dtype(df[field]):
                        df[field].fillna(df[field].mean(), inplace=True)
                    else:
                        df[field].fillna(df[field].mode().iloc[0], inplace=True)
                elif strategy == "Predictive Model":
                    from sklearn.impute import KNNImputer
                    imputer = KNNImputer(n_neighbors=5)
                    df[[field]] = imputer.fit_transform(df[[field]])
                elif strategy == "Deletion":
                    df.dropna(subset=[field], inplace=True)
                elif strategy == "Manual Input":
                    manual_value = manual_inputs.get(field)
                    if manual_value is not None:
                        df[field].fillna(manual_value, inplace=True)

        # Fix PII data
        if pii_actions:
            for field, action in pii_actions.items():
                if action == "Remove Field":
                    df.drop(columns=[field], inplace=True)
                    record_action(f"Removed PII field '{field}' from '{file_path}'")
                elif action == "Anonymize Field":
                    df[field] = df[field].apply(lambda x: hash(str(x)))
                    record_action(f"Anonymized PII field '{field}' in '{file_path}'")

        fix_functions = {
            "Non-ASCII characters in column": fix_non_ascii_characters,
            "Inconsistent or invalid date formats in column": fix_inconsistent_dates,
            "Negative values in column": fix_negative_values,
            # Add more mappings as needed
        }

        # Fix discrepancies
        if discrepancies:
            for discrepancy in discrepancies:
                for discrepancy_type, fix_function in fix_functions.items():
                    if discrepancy_type in discrepancy:
                        match = re.search(rf"{re.escape(discrepancy_type)} '(.+)'", discrepancy)
                        if match:
                            column = match.group(1)
                            df = fix_function(df, column)
                            record_action(f"Applied fix for '{discrepancy_type}' in column '{column}' in '{file_path}'")
                        else:
                            log_error(f"Could not parse column name from discrepancy: {discrepancy}")
                        break  # Exit the inner loop once a match is found
        # Add more discrepancy fixes as needed

        # Save the modified DataFrame back to a CSV file
        saved_path = save_file(df, file_path)

        # Re-extract hierarchy after fixing data
        df_fixed, _ = read_file(saved_path)
        hierarchy = extract_hierarchy(df_fixed)
        hierarchy_path = os.path.join(
            os.path.dirname(saved_path),
            f"{os.path.basename(saved_path).replace('.', '_')}_hierarchy.png"
        )
        if len(hierarchy.nodes) > 0:
            visualize_hierarchy(hierarchy, save_path=hierarchy_path)
        else:
            log_event(f"No hierarchy detected in '{file_path}'")

        return True, hierarchy

    except Exception as e:
        log_error(f"Data Import - Error fixing data in '{file_path}': {str(e)}")
        record_action(f"Error applying data fixes to '{file_path}': {str(e)}")
        return False, None

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    discrepancies = []
    # Configurable list for negative value checks
    non_negative_columns = ['age', 'quantity', 'price']  # Update as needed

    for column in df.columns:
        try:
            # Check for non-ASCII characters
            if df[column].dtype == object and df[column].str.contains(r'[^\x00-\x7F]', na=False).any():
                discrepancies.append(f"Non-ASCII characters in column '{column}'")

            # Check for inconsistent date formats
            if df[column].dtype == object:
                non_null_values = df[column].dropna()
                if not non_null_values.empty:
                    # Infer date formats for each value
                    date_formats = non_null_values.apply(infer_date_format)
                    unique_formats = date_formats.dropna().unique()
                    if len(unique_formats) > 1:
                        discrepancies.append(f"Inconsistent date formats in column '{column}'")

            # Check for negative values in numeric columns
            if pd.api.types.is_numeric_dtype(df[column]) and column in non_negative_columns:
                if (df[column] < 0).any():
                    discrepancies.append(f"Negative values in column '{column}'")

            # Add more discrepancy checks as needed

        except Exception as e:
            log_error(f"Error processing column '{column}': {str(e)}")
            # Optionally, convert unhashable types in this column to strings
            df[column] = df[column].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

    return discrepancies if discrepancies else None

def infer_date_format(date_str):
    """
    Infer the date format from a date string.
    Returns the format string if successful, else returns None.
    """
    from datetime import datetime

    known_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
        # Add more formats as needed
    ]
    for fmt in known_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return fmt
        except ValueError:
            continue
    return None