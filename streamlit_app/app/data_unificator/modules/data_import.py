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
)
from data_unificator.utils.logging_utils import log_event, log_error
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
        # Detect encoding
        encoding = detect_encoding(file_path)
        record_action(f"Detected encoding '{encoding}' for file '{file_path}'")

        # Read file
        df = read_file(file_path, encoding)

        # Sanitize data to prevent code execution, memory overflow, etc.
        df = sanitize_data(df)

        # Remove duplicates
        df = remove_duplicates_in_df(df)

        # Check for discrepancies
        discrepancies = find_discrepancies(df)
        if discrepancies:
            # Inform user via GUI (handled in import_ui.py)
            record_action(f"Discrepancies found in file '{file_path}': {discrepancies}")
            return {"status": "discrepancy", "file": file_path, "data": df, "discrepancies": discrepancies}

        # Check for missing data
        missing_data_info = df.isnull().sum()
        if missing_data_info.any():
            # Inform user via GUI (handled in import_ui.py)
            record_action(f"Missing data found in file '{file_path}': {missing_data_info.to_dict()}")
            return {"status": "missing_data", "file": file_path, "data": df, "missing_data_info": missing_data_info}

        # Check for PII
        pii_fields = check_for_pii(df)
        if pii_fields:
            # Inform user via GUI (handled in import_ui.py)
            record_action(f"PII data found in file '{file_path}': {pii_fields}")
            return {"status": "pii_found", "file": file_path, "data": df, "pii_fields": pii_fields}

        # Perform EDA
        eda_report = perform_eda(df, file_path)
        record_action(f"EDA performed on file '{file_path}'")

        return {"status": "success", "file": file_path, "data": df, "eda_report": eda_report}

    except Exception as e:
        error_message = f"Error importing file '{file_path}': {str(e)}"
        log_error(error_message)
        record_action(error_message)
        traceback_str = traceback.format_exc()
        log_error(traceback_str)
        return {"status": "error", "file": file_path, "error": error_message}

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    # Implement logic to find discrepancies, e.g., inconsistent data types
    discrepancies = []
    for column in df.columns:
        if df[column].dtype == object:
            if df[column].str.contains(r'[^\x00-\x7F]').any():
                discrepancies.append(f"Non-ASCII characters in column '{column}'")
    return discrepancies if discrepancies else None
