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
from data_unificator.utils.data_utils import (
    perform_eda,
    extract_hierarchy,
    extract_hierarchy_from_data_structure,
    visualize_hierarchy
)
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
    file_extension = os.path.splitext(file_name)[1].lower()
    discrepancies = None
    missing_data_info = None
    pii_fields = None
    eda_report = None

    try:
        # Detect encoding
        encoding = detect_encoding(file_path)
        record_action(f"Detected encoding '{encoding}' for file '{file_path}'")

        # Read the file
        data_or_df, skipped = read_file(file_path, encoding, return_as_df=(file_extension not in ['.json', '.xml']))
        skipped_entries += skipped
        if data_or_df is None or (isinstance(data_or_df, pd.DataFrame) and data_or_df.empty):
            error_message = f"File read error - '{file_path}'"
            log_error(error_message)
            record_action(error_message)
            return {
                "status": "error",
                "file": file_name,
                "error": error_message,
                "file_path": file_path,
                "file_extension": file_extension,
                "skipped_entries": skipped_entries
            }

        if file_extension in ['.json', '.xml']:
            data = data_or_df
            # Check for discrepancies in data structures
            discrepancies = find_discrepancies_in_structure(data)
            # Check for missing data
            missing_data_info = find_missing_data_in_structure(data)
            # Check for PII
            pii_fields = check_for_pii_in_structure(data)
        else:
            df = data_or_df
            # Sanitize data
            df = df.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            df.columns = [str(col) for col in df.columns]
            df = sanitize_data(df)
            df = remove_duplicates_in_df(df)
            discrepancies = find_discrepancies(df)
            if df.isnull().values.any():
                missing_data_info = df.isnull().sum()
                missing_data_info = missing_data_info[missing_data_info > 0]
                record_action(f"Missing data found in file '{file_path}': {missing_data_info.to_dict()}")
            pii_fields = check_for_pii(df)
            if pii_fields:
                record_action(f"PII data found in file '{file_path}': {pii_fields}")

        # If there are any issues, return with status 'issues_found'
        if discrepancies or (
            missing_data_info is not None and (
                (isinstance(missing_data_info, pd.Series) and not missing_data_info.empty) or
                (isinstance(missing_data_info, dict) and bool(missing_data_info))
            )
        ) or pii_fields:
            return {
                "status": "issues_found",
                "file": file_name,
                "file_path": file_path,
                "file_extension": file_extension,
                "data": data_or_df,
                "discrepancies": discrepancies,
                "missing_data_info": missing_data_info,
                "pii_fields": pii_fields,
                "skipped_entries": skipped_entries
            }

        # No issues found, proceed to perform hierarchy extraction and EDA

        # Perform hierarchy extraction
        if file_extension in ['.json', '.xml']:
            hierarchy = extract_hierarchy_from_data_structure(data)
        else:
            hierarchy = extract_hierarchy(df)
        hierarchy_path = os.path.join(
            base_path, f"{file_name.replace('.', '_')}_hierarchy.png"
        )
        visualize_hierarchy(hierarchy, save_path=hierarchy_path)

        # Perform EDA for tabular data
        if file_extension not in ['.json', '.xml']:
            eda_report = perform_eda(df, file_path)
            record_action(f"EDA performed on file '{file_path}'")

        # Backup the original file
        backup_folder = os.path.join(base_path, "backup")
        os.makedirs(backup_folder, exist_ok=True)
        backup_file(file_path, backup_folder)

        # Return success status along with hierarchy data
        return {
            "status": "success",
            "file": file_name,
            "file_path": file_path,
            "file_extension": file_extension,
            "data": data_or_df,
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
            "file_extension": file_extension,
            "error": error_message,
            "skipped_entries": skipped_entries
        }

def find_discrepancies_in_structure(data):
    discrepancies = []
    non_negative_fields = ['age', 'quantity', 'price']  # Update as needed

    def traverse(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                check_value_discrepancies(value, current_path)
                traverse(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                check_value_discrepancies(item, current_path)
                traverse(item, current_path)
        else:
            pass  # Leaf node

    def check_value_discrepancies(value, path):
        # Check for non-ASCII characters
        if isinstance(value, str):
            if re.search(r'[^\x00-\x7F]', value):
                discrepancies.append(f"Non-ASCII characters at '{path}'")
            #if infer_date_format(value) is None and is_possible_date(value):  # pending test of infer_date_format
                #discrepancies.append(f"Inconsistent date format at '{path}'")
        elif isinstance(value, (int, float)):
            field_name = path.split('.')[-1]
            if field_name in non_negative_fields and value < 0:
                discrepancies.append(f"Negative value at '{path}'")

    def is_possible_date(value):
        return bool(re.match(r'\d{1,4}[/-]\d{1,2}[/-]\d{1,4}', value))

    traverse(data)
    return discrepancies if discrepancies else None

def find_missing_data_in_structure(data):
    missing_data_info = {}

    def traverse(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    missing_data_info[current_path] = missing_data_info.get(current_path, 0) + 1
                else:
                    traverse(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse(item, current_path)
        else:
            pass  # Leaf node

    traverse(data)
    return missing_data_info if missing_data_info else None

def check_for_pii_in_structure(data):
    pii_fields = []
    potential_pii_keywords = ['ssn', 'passport', 'credit_card', 'email', 'phone']  # Update as needed

    def traverse(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if any(keyword in key.lower() for keyword in potential_pii_keywords):
                    pii_fields.append(current_path)
                traverse(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                traverse(item, path)
        else:
            pass  # Leaf node

    traverse(data)
    return pii_fields if pii_fields else None

def apply_data_fixes(file_path, missing_data_strategies=None, manual_inputs=None, pii_actions=None, discrepancies=None):
    """
    Apply the selected data fixes to the file, including missing data, PII, and discrepancies.
    """
    try:
        # Backup the original file before applying data fixes
        backup_folder = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_folder, exist_ok=True)
        backup_file(file_path, backup_folder)
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.json', '.xml']:
            data, skipped_entries = read_file(file_path, return_as_df=False)
            if data is None:
                error_message = f"File error - {file_path}"
                log_error(error_message)
                record_action(error_message)
                return False, None

            # Apply data fixes directly on data structure
            data = apply_fixes_to_data_structure(
                data,
                missing_data_strategies=missing_data_strategies,
                manual_inputs=manual_inputs,
                pii_actions=pii_actions,
                discrepancies=discrepancies
            )

            # Save the modified data back to the original file
            saved_path = save_file(data, file_path, data_structure=True)

            # Re-extract hierarchy after fixing data
            hierarchy = extract_hierarchy_from_data_structure(data)
            hierarchy_path = os.path.join(
                os.path.dirname(saved_path),
                f"{os.path.basename(saved_path).replace('.', '_')}_hierarchy.png"
            )
            visualize_hierarchy(hierarchy, save_path=hierarchy_path)

        else:
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
                "Inconsistent date formats in column": fix_inconsistent_dates,
                "Negative values in column": fix_negative_values,
                # Add more mappings as needed
            }

            # Fix discrepancies
            if discrepancies:
                for discrepancy in discrepancies:
                    for discrepancy_type, fix_function in fix_functions.items():
                        if discrepancy_type in discrepancy:
                            match = re.search(rf"{re.escape(discrepancy_type)} in column '(.+)'", discrepancy)
                            if match:
                                column = match.group(1)
                                df = fix_function(df, column)
                                record_action(f"Applied fix for '{discrepancy_type}' in column '{column}' in '{file_path}'")
                            else:
                                log_error(f"Could not parse column name from discrepancy: {discrepancy}")
                            break  # Exit the inner loop once a match is found

            # Save the modified DataFrame back to the file
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

def convert_json_xml_to_csv(file_paths):
    """
    Convert JSON and XML files to CSV format.
    """
    converted_files = []
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.json', '.xml']:
            continue
        try:
            # Backup the original file
            base_path = os.path.dirname(file_path)
            backup_folder = os.path.join(base_path, "backup")
            os.makedirs(backup_folder, exist_ok=True)
            backup_file(file_path, backup_folder)

            # Read the file
            data_or_df, skipped = read_file(file_path, return_as_df=True)
            if isinstance(data_or_df, pd.DataFrame):
                # Save as CSV
                csv_path = os.path.splitext(file_path)[0] + '.csv'
                save_file(data_or_df, csv_path, as_csv=True)
                converted_files.append(csv_path)
                # Remove original file
                os.remove(file_path)
                record_action(f"Converted '{file_path}' to '{csv_path}' and removed original file.")
            else:
                log_error(f"Cannot convert non-tabular file '{file_path}' to CSV.")
        except Exception as e:
            log_error(f"Error converting file '{file_path}' to CSV: {str(e)}")
            record_action(f"Error converting file '{file_path}' to CSV: {str(e)}")
    return converted_files

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    discrepancies = []
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
                    date_formats = non_null_values.apply(infer_date_format)
                    unique_formats = date_formats.dropna().unique()
                    #if len(unique_formats) > 1: # pending test of infer_date_format
                        #discrepancies.append(f"Inconsistent date formats in column '{column}'")

            # Check for negative values in numeric columns
            if pd.api.types.is_numeric_dtype(df[column]) and column in non_negative_columns:
                if (df[column] < 0).any():
                    discrepancies.append(f"Negative values in column '{column}'")

        except Exception as e:
            log_error(f"Error processing column '{column}': {str(e)}")
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

def apply_fixes_to_data_structure(data, missing_data_strategies=None, manual_inputs=None, pii_actions=None, discrepancies=None):
    # Fix missing data
    if missing_data_strategies:
        data = fix_missing_data_in_structure(data, missing_data_strategies, manual_inputs)

    # Fix PII data
    if pii_actions:
        data = fix_pii_in_structure(data, pii_actions)

    # Fix discrepancies
    if discrepancies:
        data = fix_discrepancies_in_structure(data, discrepancies)

    return data

def fix_missing_data_in_structure(data, missing_data_strategies, manual_inputs):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                value = data[key]
                strategy = missing_data_strategies.get(current_path)
                if strategy:
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        if strategy == "Deletion":
                            del data[key]
                        elif strategy == "Manual Input":
                            manual_value = manual_inputs.get(current_path)
                            if manual_value is not None:
                                data[key] = manual_value
                    else:
                        traverse_and_fix(value, current_path)
                else:
                    traverse_and_fix(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    traverse_and_fix(data)
    return data

def fix_pii_in_structure(data, pii_actions):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                action = pii_actions.get(current_path)
                if action:
                    if action == "Remove Field":
                        del data[key]
                    elif action == "Anonymize Field":
                        data[key] = hash(str(data[key]))
                else:
                    traverse_and_fix(data[key], current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    traverse_and_fix(data)
    return data

def fix_discrepancies_in_structure(data, discrepancies):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                value = data[key]
                # Check for discrepancies
                if f"Non-ASCII characters at '{current_path}'" in discrepancies:
                    from unidecode import unidecode
                    if isinstance(value, str):
                        data[key] = unidecode(value)
                if f"Inconsistent date format at '{current_path}'" in discrepancies:
                    if isinstance(value, str):
                        standardized_date = standardize_date(value)
                        if standardized_date:
                            data[key] = standardized_date
                if f"Negative value at '{current_path}'" in discrepancies:
                    if isinstance(value, (int, float)):
                        data[key] = abs(value)
                # Recurse
                traverse_and_fix(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    def standardize_date(date_str):
        from datetime import datetime
        target_format = "%Y-%m-%d"
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
        ]
        for fmt in known_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(target_format)
            except ValueError:
                continue
        return date_str

    traverse_and_fix(data)
    return data

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

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    discrepancies = []
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
                    date_formats = non_null_values.apply(infer_date_format)
                    unique_formats = date_formats.dropna().unique()
                    #if len(unique_formats) > 1: # pending test of infer_date_format
                        #discrepancies.append(f"Inconsistent date formats in column '{column}'")

            # Check for negative values in numeric columns
            if pd.api.types.is_numeric_dtype(df[column]) and column in non_negative_columns:
                if (df[column] < 0).any():
                    discrepancies.append(f"Negative values in column '{column}'")

        except Exception as e:
            log_error(f"Error processing column '{column}': {str(e)}")
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

def apply_fixes_to_data_structure(data, missing_data_strategies=None, manual_inputs=None, pii_actions=None, discrepancies=None):
    # Fix missing data
    if missing_data_strategies:
        data = fix_missing_data_in_structure(data, missing_data_strategies, manual_inputs)

    # Fix PII data
    if pii_actions:
        data = fix_pii_in_structure(data, pii_actions)

    # Fix discrepancies
    if discrepancies:
        data = fix_discrepancies_in_structure(data, discrepancies)

    return data

def fix_missing_data_in_structure(data, missing_data_strategies, manual_inputs):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                value = data[key]
                strategy = missing_data_strategies.get(current_path)
                if strategy:
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        if strategy == "Deletion":
                            del data[key]
                        elif strategy == "Manual Input":
                            manual_value = manual_inputs.get(current_path)
                            if manual_value is not None:
                                data[key] = manual_value
                    else:
                        traverse_and_fix(value, current_path)
                else:
                    traverse_and_fix(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    traverse_and_fix(data)
    return data

def fix_pii_in_structure(data, pii_actions):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                action = pii_actions.get(current_path)
                if action:
                    if action == "Remove Field":
                        del data[key]
                    elif action == "Anonymize Field":
                        data[key] = hash(str(data[key]))
                else:
                    traverse_and_fix(data[key], current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    traverse_and_fix(data)
    return data

def fix_discrepancies_in_structure(data, discrepancies):
    def traverse_and_fix(data, path=""):
        if isinstance(data, dict):
            for key in list(data.keys()):
                current_path = f"{path}.{key}" if path else key
                value = data[key]
                # Check for discrepancies
                if f"Non-ASCII characters at '{current_path}'" in discrepancies:
                    from unidecode import unidecode
                    if isinstance(value, str):
                        data[key] = unidecode(value)
                if f"Inconsistent date format at '{current_path}'" in discrepancies:
                    if isinstance(value, str):
                        standardized_date = standardize_date(value)
                        if standardized_date:
                            data[key] = standardized_date
                if f"Negative value at '{current_path}'" in discrepancies:
                    if isinstance(value, (int, float)):
                        data[key] = abs(value)
                # Recurse
                traverse_and_fix(value, current_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                current_path = f"{path}[{index}]"
                traverse_and_fix(item, current_path)
        else:
            pass  # Leaf node

    def standardize_date(date_str):
        from datetime import datetime
        target_format = "%Y-%m-%d"
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
        ]
        for fmt in known_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(target_format)
            except ValueError:
                continue
        return date_str

    traverse_and_fix(data)
    return data

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

def find_discrepancies(df):
    """
    Identify discrepancies in the DataFrame.
    """
    discrepancies = []
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
                    date_formats = df[column].apply(infer_date_format)
                    unique_formats = date_formats.dropna().unique()
                    #if len(unique_formats) > 1: # pending test of infer_date_format
                        #discrepancies.append(f"Inconsistent date formats in column '{column}'")

            # Check for negative values in numeric columns
            if pd.api.types.is_numeric_dtype(df[column]) and column in non_negative_columns:
                if (df[column] < 0).any():
                    discrepancies.append(f"Negative values in column '{column}'")

        except Exception as e:
            log_error(f"Error processing column '{column}': {str(e)}")
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

