# utils/file_utils.py

import os
import pandas as pd
import chardet
from data_unificator.utils.logging_utils import log_error
from data_unificator.config import ConfigManager

config_manager = ConfigManager()

def get_supported_files(folder_path):
    """
    Retrieve a list of supported files from the specified folder.
    """
    supported_formats = config_manager.get('data_import', 'supported_formats', [])
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in supported_formats):
                files.append(os.path.join(root, filename))
    return files

def read_file(file_path, encoding='utf-8'):
    """
    Read a file into a Pandas DataFrame based on its extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv' or ext == '.tsv':
            sep = ',' if ext == '.csv' else '\t'
            return pd.read_csv(file_path, encoding=encoding, sep=sep)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)
        elif ext == '.json':
            return pd.read_json(file_path, encoding=encoding)
        elif ext == '.xml':
            return pd.read_xml(file_path)
        elif ext == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        log_error(f"Error reading file '{file_path}': {str(e)}")
        raise e

def detect_encoding(file_path):
    """
    Detect the character encoding of a file.
    """
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(100000))
            return result['encoding']
    except Exception as e:
        log_error(f"Error detecting encoding for '{file_path}': {str(e)}")
        return config_manager.get('data_import', 'default_encoding', 'utf-8')

def remove_duplicates_in_df(df):
    """
    Remove duplicate rows from a DataFrame.
    """
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    return df, duplicates_removed

def check_for_pii(df):
    """
    Check for Personal Identifiable Information (PII) in the DataFrame.
    """
    pii_fields = []
    potential_pii_columns = ['name', 'email', 'address', 'ssn', 'phone', 'passport', 'credit_card']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in potential_pii_columns):
            pii_fields.append(col)
    return pii_fields if pii_fields else None
