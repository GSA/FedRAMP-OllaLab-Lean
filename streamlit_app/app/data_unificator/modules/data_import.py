# modules/data_import.py

import os
import pandas as pd
import logging
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
from data_unificator.utils.logging_utils import log_error
from data_unificator.utils.security_utils import sanitize_data
from data_unificator.utils.eda_utils import perform_eda
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
    try:
        # Backup the original file before processing
        backup_file(file_path, "backup")

        # Detect encoding
        encoding = detect_encoding(file_path)
        record_action(f"Detected encoding '{encoding}' for file '{file_path}'")

        # Read the file
        df = read_file(file_path, encoding)
        if df is None or df.empty:
            error_message = f"File '{file_path}' is empty or could not be read."
            log_error(error_message)
            record_action(error_message)
            return {"status": "error", "file": os.path.basename(file_path), "error": error_message}

        # Sanitize data to prevent issues like memory overflow
        df = sanitize_data(df)

        # Remove duplicates
        df = remove_duplicates_in_df(df)

        # Check for discrepancies
        discrepancies = find_discrepancies(df)
        if discrepancies:
            record_action(f"Discrepancies found in file '{file_path}': {discrepancies}")
            return {"status": "discrepancy", "file": os.path.basename(file_path), "data": df, "discrepancies": discrepancies}

        # Check for missing data and show missing value counts per field
        if df.isnull().values.any():
            missing_data_info = df.isnull().sum()
            missing_data_counts = missing_data_info[missing_data_info > 0]
            record_action(f"Missing data found in file '{file_path}': {missing_data_counts.to_dict()}")
            return {"status": "missing_data", "file": os.path.basename(file_path), "data": df, "missing_data_info": missing_data_counts}

        # Check for PII
        pii_fields = check_for_pii(df)
        if pii_fields:
            record_action(f"PII data found in file '{file_path}': {pii_fields}")
            return {"status": "pii_found", "file": os.path.basename(file_path), "data": df, "pii_fields": pii_fields}

        # Perform EDA
        eda_report = perform_eda(df, file_path)
        record_action(f"EDA performed on file '{file_path}'")

        return {"status": "success", "file": os.path.basename(file_path), "data": df, "eda_report": eda_report}

    except Exception as e:
        error_message = f"Error importing file '{file_path}': {str(e)}"
        log_error(error_message)
        record_action(error_message)
        traceback_str = traceback.format_exc()
        log_error(traceback_str)
        return {"status": "error", "file": os.path.basename(file_path), "error": error_message}

def apply_missing_data_strategy(file_path, strategy, manual_inputs=None):
    """
    Apply the selected missing data handling strategy to the file.
    """
    try:
        # Backup the original file before applying missing data strategy
        backup_file(file_path, "backup")

        # Read the file into a DataFrame
        df = read_file(file_path)
        if df is None or df.empty:
            error_message = f"File '{file_path}' is empty or could not be read."
            log_error(error_message)
            record_action(error_message)
            return False

        # Handle different missing data strategies
        if strategy == "Statistical Imputation":
            df_numeric = df.select_dtypes(include=[pd.np.number])
            if not df_numeric.empty:
                df[df_numeric.columns] = df_numeric.fillna(df_numeric.mean())
            df_categorical = df.select_dtypes(include=['object'])
            if not df_categorical.empty:
                df[df_categorical.columns] = df_categorical.fillna(df_categorical.mode().iloc[0])

        elif strategy == "Predictive Model":
            from sklearn.impute import KNNImputer
            df_numeric = df.select_dtypes(include=[pd.np.number])
            if not df_numeric.empty:
                imputer = KNNImputer(n_neighbors=5)
                df[df_numeric.columns] = imputer.fit_transform(df_numeric)
            df_categorical = df.select_dtypes(include=['object'])
            if not df_categorical.empty:
                df[df_categorical.columns] = df_categorical.fillna(df_categorical.mode().iloc[0])

        elif strategy == "Deletion":
            df = df.dropna()

        elif strategy == "Manual Input":
            # Allow the user to manually input values for fields with missing data
            for field, manual_value in manual_inputs.items():
                if manual_value:
                    df[field] = df[field].fillna(manual_value)

        # Save the modified DataFrame back to the file
        save_file(df, file_path)
        return True

    except Exception as e:
        log_error(f"Error applying missing data strategy '{strategy}' to '{file_path}': {str(e)}")
        record_action(f"Error applying missing data strategy '{strategy}' to '{file_path}': {str(e)}")
        return False

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    # Implement logic to find discrepancies, e.g., inconsistent data types or invalid values
    discrepancies = []
    for column in df.columns:
        if df[column].dtype == object and df[column].str.contains(r'[^\x00-\x7F]', na=False).any():
            discrepancies.append(f"Non-ASCII characters in column '{column}'")
    return discrepancies if discrepancies else None
