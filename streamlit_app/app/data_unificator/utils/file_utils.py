# utils/file_utils.py

import os
import pandas as pd
import chardet
import shutil
import xml.etree.ElementTree as ET
import json
import re
from pandas import json_normalize
from typing import Iterator, Optional
from collections.abc import Hashable
from data_unificator.utils.logging_utils import log_error, log_event
from data_unificator.config import ConfigManager

config_manager = ConfigManager()

def get_supported_files(folder_path, exclude_backup=False):
    """
    Retrieve a list of supported files from the specified folder.
    Optionally, exclude the 'backup' folder and its contents.

    :param folder_path: Path to the folder where files are stored.
    :param exclude_backup: If True, exclude files in the 'backup' folder.
    :return: List of supported file paths.
    """
    supported_formats = config_manager.get('data_import', 'supported_formats', [])
    if not supported_formats:
        # Default supported formats if not specified in the config
        supported_formats = ['.csv', '.tsv', '.xls', '.xlsx', '.json', '.xml', '.parquet']
    files = []
    for root, _, filenames in os.walk(folder_path):
        # Exclude the backup folder if specified
        if exclude_backup and 'backup' in root.lower():
            continue
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in supported_formats):
                files.append(os.path.join(root, filename))
    return files

def read_file(file_path, encoding=None):
    """
    Read a file into a Pandas DataFrame based on its extension.

    :param file_path: Path to the file to be read.
    :param encoding: Character encoding to use (optional).
    :return: DataFrame with the contents of the file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if encoding is None:
        encoding = detect_encoding(file_path)
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path, encoding=encoding)
            skipped_entries = 0
        elif ext == '.tsv':
            df = pd.read_csv(file_path, encoding=encoding, sep='\t')
            skipped_entries = 0
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            skipped_entries = 0
        elif ext == '.json':
            df, skipped_entries = read_json_file(file_path)
        elif ext == '.xml':
            df, skipped_entries = read_xml_file(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
            skipped_entries = 0
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return df, skipped_entries
    except Exception as e:
        log_error(f"Error reading file '{file_path}': {str(e)}")
        raise e

def read_json_file(file_path: str, chunk_size: int = 1000):
    """
    Read a JSON file into a DataFrame, properly handling complex nested structures.

    :param file_path: Path to the JSON file.
    :param chunk_size: The number of records to read per iteration.
    :return: A DataFrame containing the JSON data and the number of skipped entries.
    """
    skipped_entries = 0  # Initialize skipped entries counter
    records = []
    all_data = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Attempt to load the entire file as standard JSON
            try:
                data = json.load(f)
                line_delimited = False
            except json.JSONDecodeError:
                # If loading fails, assume it's line-delimited JSON
                line_delimited = True

        if not line_delimited:
            # Process standard JSON file
            if isinstance(data, dict):
                # Check if 'results' key exists, adjust as necessary for your data
                if 'results' in data:
                    df = pd.json_normalize(
                        data,
                        record_path=['results'],
                        sep='.',
                        max_level=None
                    )
                else:
                    # Flatten the entire dictionary
                    df = pd.json_normalize(data, sep='.')
            elif isinstance(data, list):
                # If the root is a list, normalize it directly
                df = pd.json_normalize(data, sep='.')
            else:
                log_error(f"JSON - Unsupported structure in file - {file_path}")
                return pd.DataFrame(), skipped_entries

            # Sanitize column names
            df.columns = sanitize_field_names(df.columns)
            # Sanitize cell data
            df = df.applymap(sanitize_cell_data)

            return df, skipped_entries
        else:
            # Process line-delimited JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        records.append(record)
                        if len(records) >= chunk_size:
                            df_chunk = pd.json_normalize(records, sep='.')
                            df_chunk.columns = sanitize_field_names(df_chunk.columns)
                            df_chunk = df_chunk.applymap(sanitize_cell_data)
                            all_data.append(df_chunk)
                            records = []
                    except json.JSONDecodeError as e:
                        log_error(f"JSON - Decoder error - {str(e)} - {file_path}")
                        skipped_entries += 1

                # Process any remaining records
                if records:
                    df_chunk = pd.json_normalize(records, sep='.')
                    df_chunk.columns = sanitize_field_names(df_chunk.columns)
                    df_chunk = df_chunk.applymap(sanitize_cell_data)
                    all_data.append(df_chunk)

            if all_data:
                final_df = pd.concat(all_data, ignore_index=True)
                return final_df, skipped_entries
            else:
                log_error(f"JSON - No data processed - {file_path}")
                return pd.DataFrame(), skipped_entries

    except FileNotFoundError:
        log_error(f"JSON - File not found - {file_path}")
        return pd.DataFrame(), skipped_entries
    except Exception as e:
        log_error(f"JSON - Other error - {str(e)} - {file_path}")
        return pd.DataFrame(), skipped_entries


def sanitize_cell_data(x):
    """
    Sanitize cell data by converting lists and dicts to strings.

    :param x: Cell data.
    :return: Sanitized cell data.
    """
    if isinstance(x, list):
        return ', '.join(map(str, x))
    elif isinstance(x, dict):
        return json.dumps(x)
    else:
        return x


def read_xml_file(xml_file):
    """
    Read an XML file into a Pandas DataFrame.

    :param xml_file: Path to the XML file.
    :return: DataFrame with the contents of the XML file and the number of skipped entries.
    """
    skipped_entries = 0  # Initialize skipped entries counter

    def parse_element(element, parent_path=""):
        """
        Recursively parse XML elements and store them in a list of dictionaries.
        """
        rows = []
        current_path = f"{parent_path}/{element.tag}" if parent_path else element.tag
        row = {}
        # Store element's attributes
        for key, value in element.attrib.items():
            row[f"{current_path}@{key}"] = value
        # Store element text (if any)
        text = element.text.strip() if element.text else ''
        if text:
            row[current_path] = text
        # Recursively parse child elements
        try:
            child_rows = []
            for child in element:
                child_rows.extend(parse_element(child, current_path))
            if child_rows:
                for child_row in child_rows:
                    combined_row = row.copy()
                    combined_row.update(child_row)
                    rows.append(combined_row)
            else:
                rows.append(row)
        except Exception as e:
            log_error(f"Data Import - XML - {str(e)}")
            skipped_entries += 1
        return rows

    # Parse the XML file
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # Parse root into data rows
        rows = parse_element(root)
        # Convert dict to DataFrame
        if rows:
            df = pd.DataFrame(rows)
            df.columns = sanitize_field_names(df.columns)
        else:
            df = pd.DataFrame()
    except FileNotFoundError:
        log_error(f"XML - File not found - {xml_file}")
        return pd.DataFrame(), skipped_entries
    except ET.ParseError as e:
        log_error(f"XML - Parsing error - {str(e)} - {xml_file}")
        return pd.DataFrame(), skipped_entries
    except Exception as e:
        log_error(f"XML - Other error - {str(e)} - {xml_file}")
        return pd.DataFrame(), skipped_entries
    return df, skipped_entries

def detect_encoding(file_path):
    """
    Detect the character encoding of a file.

    :param file_path: Path to the file for which encoding is detected.
    :return: Detected encoding or default encoding.
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(100000)
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or config_manager.get('data_import', 'default_encoding', 'utf-8')
            return encoding
    except Exception as e:
        log_error(f"Error detecting encoding for '{file_path}': {str(e)}")
        return config_manager.get('data_import', 'default_encoding', 'utf-8')

def save_file(df, file_path, as_csv=True):
    """
    Save a DataFrame back to a file based on its extension.

    :param df: DataFrame to save.
    :param file_path: Path to the file.
    :param as_csv: If True, save the DataFrame as a CSV file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            log_event(f"Removed original file '{file_path}' before saving fixed content.")
        if as_csv or ext == '.csv':
            # Force save as CSV if `as_csv` is True or original file is CSV
            csv_path = os.path.splitext(file_path)[0] + ".csv"
            df.to_csv(csv_path, index=False)
            if as_csv and ext != '.csv':
                log_event(f"File saved as CSV: {csv_path}")
            return csv_path
        elif ext == '.tsv':
            df.to_csv(file_path, sep='\t', index=False)
            return file_path
        elif ext in ['.xls', '.xlsx']:
            df.to_excel(file_path, index=False)
            return file_path
        elif ext == '.json':
            df.to_json(file_path, orient='records', lines=True)
            return file_path
        elif ext == '.xml':
            df.to_xml(file_path, index=False)
            return file_path
        elif ext == '.parquet':
            df.to_parquet(file_path, index=False)
            return file_path
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        log_error(f"Error saving file '{file_path}': {str(e)}")
        raise e

def remove_duplicates_in_df(df):
    """
    Remove duplicate rows from a DataFrame.

    :param df: DataFrame from which duplicates are to be removed.
    :return: DataFrame with duplicates removed.
    """
    try:
        # Ensure all columns are hashable
        df.columns = [str(col) if not isinstance(col, Hashable) else col for col in df.columns]
        df = df.drop_duplicates()
    except TypeError as e:
        log_error(f"Data Import - Error with removing duplicates: {str(e)}")
        # Convert all cells to strings
        df = df.applymap(lambda x: str(x) if not isinstance(x, Hashable) else x)
        df = df.drop_duplicates()
    return df

def check_for_pii(df):
    """
    Check for Personal Identifiable Information (PII) in the DataFrame.

    :param df: DataFrame to check for PII.
    :return: List of column names that potentially contain PII.
    """
    pii_fields = []
    potential_pii_columns = ['ssn', 'passport', 'credit_card']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in potential_pii_columns):
            pii_fields.append(col)
    return pii_fields if pii_fields else None

def backup_file(file_path, backup_folder):
    """
    Backup the file to the specified backup folder.

    :param file_path: Path to the file to be backed up.
    :param backup_folder: Folder where the backup will be stored.
    """
    try:
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        backup_path = os.path.join(backup_folder, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)  # Changed from shutil.move to shutil.copy2
        log_event(f"File '{file_path}' copied to '{backup_path}'")
    except Exception as e:
        log_error(f"Error backing up file '{file_path}' to '{backup_folder}': {str(e)}")
        raise e

def sanitize_field_names(field_names):
    """
    Sanitize field names to ensure they contain only letters, numbers, and periods.
    Convert '/' and '\' to '.' and ensure the leading character of each field name is an alphabet.

    :param field_names: A list or index of field names (columns).
    :return: Sanitized field names.
    """
    sanitized_names = []
    for field_name in field_names:
        # Convert field_name to string if it's not
        if not isinstance(field_name, str):
            field_name = str(field_name)
        # Replace '/' and '\' with a dot
        sanitized_name = field_name.replace('/', '.').replace('\\', '.')
        # Replace any character that is not a letter, number, or period with an underscore
        sanitized_name = re.sub(r'[^a-zA-Z0-9\.]', '_', sanitized_name)
        # Ensure the leading character is a letter (if not, prefix with 'col_')
        if not sanitized_name[0].isalpha():
            sanitized_name = 'col_' + sanitized_name
        sanitized_names.append(sanitized_name)
    return sanitized_names
