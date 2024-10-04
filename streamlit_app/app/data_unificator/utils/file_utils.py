# utils/file_utils.py

import os
import pandas as pd
import chardet
import shutil
import xml.etree.ElementTree as ET
import json
from pandas import json_normalize
from typing import Iterator, Optional
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
            return pd.read_csv(file_path, encoding=encoding)
        elif ext == '.tsv':
            return pd.read_csv(file_path, encoding=encoding, sep='\t')
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)
        elif ext == '.json':
            return read_json_file(file_path)
        elif ext == '.xml':
            return read_xml_file(file_path)
        elif ext == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        log_error(f"Error reading file '{file_path}': {str(e)}")
        raise e

def read_json_file(file_path: str, chunk_size: int = 1000, line_delimited: bool = True):
    """
    Read a large complex JSON file to a dataframe
    : param file_path: path to the json file
    : param chunk_size: The number of records to read per iteration
    : param line_delimited: True for json file that is line delimited
    : return: a pandas data frame
    """
    def process_chunk(records: list) -> pd.DataFrame:
        """
        Flatten chunks and export to data frame
        """
        return pd.concat([json_normalize(record) for record in records], ignore_index=True)
    records = []
    all_data = []
    try:
        with open(file_path, 'r') as f:
            if line_delimited:
                for line in f:
                    try:
                        record = json.loads(line.strip()) # strip newline chars
                        records.append(flat_record)
                        if len(records)  >= chunk_size:
                            df_chunk = process_chunk(records)
                            all_data.append(df_chunk)
                            records = []
            else:
                data = json.load(f)
                if isinstance(data, list): # if root object is a list
                    for record in data:
                        records.append(record)
                        if len(records) >= chunk_size:
                            df_chunk = process_chunk(records)
                            all_data.append(df_chunk)
                            records = []
                elif isinstance(data, dict): # if root object is dict
                    df_chunk = json_normalize(data)
                    all_data.append(df_chunk)
                else:
                    log_error(f"JSON - Structure not supported - {file_path}")
            if records:
                df_chunk = process_chunk(records)
                all_data.append(df_chunk)
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    except FileNotFoundError:
        log_error(f"JSON - File not found - {file_path}")
    except json.JSONDecoderError as e:
        log_error(f"JSON - Decoder error - {str(e)} - {file_path}")
    except Exception as e:
        log_error(f"JSON - Other error - {str(e)} - {file_path}")

def read_xml_file(xml_file):
    """
    Read an XML file into a Pandas DataFrame.

    :param xml_file: Path to the XML file.
    :return: DataFrame with the contents of the XML file.
    """
    def parse_element(element,parent_path=""):
        """
        Recursively parse XML elements and store them in a list of dictionaries
        """
        rows = []
        # Combine parent path with current tag
        current_path = f"{parent_path}/{element.tag}" if parent_path else elment.tag
        row = {}
        # Store element's attributes
        for key,value in element.attrib.items():
            row[f"{current_path}@{key}"]=value
        # Store element text (if any)
        if element.text and element.text.strip():
            row[current_path] = element.text.strip()
        # Recursively parse child element
        if child in element:
            child_rows = parse_element(child, current_path)
            rows.extend(child_rows)
        # If there are no child elements (a leaf node)
        if not rows:
            rows.append(row)
        else:
            for r in rows:
                r.update(row) # combine with parent element
        return rows
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Parse root into data rows
    rows = parse_element(root)
    # Convert dict to df
    df = pd.DataFrame(rows)

    return df

def detect_encoding(file_path):
    """
    Detect the character encoding of a file.

    :param file_path: Path to the file for which encoding is detected.
    :return: Detected encoding or default encoding.
    """
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(100000))
            return result['encoding'] or config_manager.get('data_import', 'default_encoding', 'utf-8')
    except Exception as e:
        log_error(f"Error detecting encoding for '{file_path}': {str(e)}")
        return config_manager.get('data_import', 'default_encoding', 'utf-8')

def save_file(df, file_path):
    """
    Save a DataFrame back to a file based on its extension.

    :param df: DataFrame to save.
    :param file_path: Path to the file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext == '.tsv':
            df.to_csv(file_path, sep='\t', index=False)
        elif ext in ['.xls', '.xlsx']:
            df.to_excel(file_path, index=False)
        elif ext == '.json':
            df.to_json(file_path, orient='records', lines=True)
        elif ext == '.xml':
            df.to_xml(file_path, index=False)
        elif ext == '.parquet':
            df.to_parquet(file_path, index=False)
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
    df = df.drop_duplicates()
    return df

def check_for_pii(df):
    """
    Check for Personal Identifiable Information (PII) in the DataFrame.

    :param df: DataFrame to check for PII.
    :return: List of column names that potentially contain PII.
    """
    pii_fields = []
    potential_pii_columns = ['name', 'email', 'address', 'ssn', 'phone', 'passport', 'credit_card']
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
        shutil.copy2(file_path, backup_path)
        log_event(f"File '{file_path}' backed up to '{backup_path}'")
    except Exception as e:
        log_error(f"Error backing up file '{file_path}' to '{backup_folder}': {str(e)}")
        raise e

