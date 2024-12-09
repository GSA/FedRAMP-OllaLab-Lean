"""
Utility functions for the Schema Extractor application.

This module provides various utility functions such as file type detection,
data backup, duplicate handling, and sensitive data detection.

Functions:
- detect_file_type(file): Detects the file type of the uploaded file.
- backup_file(file, backup_dir='backups'): Creates a backup of the uploaded file.
- handle_duplicates(data, user_choice='keep'): Detects and handles duplicates in the data.
- detect_sensitive_data(data): Detects sensitive data within the dataset.
"""
import os
import re
import pandas as pd

def detect_file_type(file):
    """
    Detects the file type of the uploaded file.

    Args:
        file (UploadedFile): The uploaded file object.

    Returns:
        str: The detected file type. One of 'tabular', 'serialized', 'unstructured', or 'unknown'.
    """
    filename = file.name
    extension = os.path.splitext(filename)[1].lower()
    extension = extension.lstrip('.')
    tabular_extensions = {'csv', 'tsv', 'xlsx', 'parquet', 'feather', 'hdf5'}
    serialized_extensions = {'json', 'xml', 'yaml', 'pickle', 'msgpack', 'bson', 'proto', 'avro'}
    unstructured_extensions = {'doc', 'docx', 'pdf', 'txt', 'md', 'log', 'rtf'}

    if extension in tabular_extensions:
        return 'tabular'
    elif extension in serialized_extensions:
        return 'serialized'
    elif extension in unstructured_extensions:
        return 'unstructured'
    else:
        return 'unknown'

def backup_file(file, backup_dir='backups'):
    """
    Creates a backup of the uploaded file.

    Args:
        file (UploadedFile): The uploaded file object.
        backup_dir (str): The directory to save backups.

    Returns:
        str: The path to the backup file.
    """
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_path = os.path.join(backup_dir, file.name)
    # Ensure unique filename in backup directory
    base, extension = os.path.splitext(backup_path)
    counter = 1
    while os.path.exists(backup_path):
        backup_path = f"{base}_{counter}{extension}"
        counter +=1
    # Write the file to backup location
    with open(backup_path, 'wb') as f:
        f.write(file.getbuffer())
    return backup_path

def handle_duplicates(data, user_choice='keep'):
    """
    Detects and handles duplicated records in the data.

    Args:
        data (DataFrame or list): The data to check for duplicates.
        user_choice (str): 'remove' to remove duplicates, 'keep' to keep duplicates.

    Returns:
        DataFrame or list: Data with duplicates handled as per user selection.

    Raises:
        ValueError: If an invalid user_choice is provided.
        TypeError: If the data type is unsupported.
    """
    if user_choice not in ['remove', 'keep']:
        raise ValueError("Invalid user_choice. Must be 'remove' or 'keep'.")

    if isinstance(data, pd.DataFrame):
        if user_choice == 'remove':
            data = data.drop_duplicates()
        # else keep data as is
    elif isinstance(data, list):
        if user_choice == 'remove':
            data = list(dict.fromkeys(data))  # Preserves order
        # else keep data as is
    else:
        # Unsupported data type
        raise TypeError("Unsupported data type for duplicate handling.")
    return data

def detect_sensitive_data(data):
    """
    Detects sensitive data within the dataset.

    Args:
        data (DataFrame, Series, list, or str): The data to scan for sensitive information.

    Returns:
        dict: Dictionary where keys are column names or indices, and values are lists of detected sensitive data elements.

    Raises:
        TypeError: If the data type is unsupported.
    """
    # Define regex patterns for sensitive data
    patterns = {
        'credit_card': re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
        'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    }

    sensitive_data = {}
    if isinstance(data, pd.DataFrame):
        for column in data.columns:
            sensitive_items = []
            for item in data[column].astype(str).fillna(''):
                for name, pattern in patterns.items():
                    if pattern.search(item):
                        sensitive_items.append({'type': name, 'value': item})
            if sensitive_items:
                sensitive_data[column] = sensitive_items
    elif isinstance(data, pd.Series):
        sensitive_items = []
        for item in data.astype(str).fillna(''):
            for name, pattern in patterns.items():
                if pattern.search(item):
                    sensitive_items.append({'type': name, 'value': item})
        if sensitive_items:
            sensitive_data['Series'] = sensitive_items
    elif isinstance(data, list):
        sensitive_items = []
        for item in data:
            item_str = str(item)
            for name, pattern in patterns.items():
                if pattern.search(item_str):
                    sensitive_items.append({'type': name, 'value': item_str})
        if sensitive_items:
            sensitive_data['List'] = sensitive_items
    elif isinstance(data, str):
        sensitive_items = []
        for name, pattern in patterns.items():
            if pattern.search(data):
                sensitive_items.append({'type': name, 'value': data})
        if sensitive_items:
            sensitive_data['String'] = sensitive_items
    else:
        # Cannot handle other data types
        raise TypeError("Unsupported data type for sensitive data detection.")
    return sensitive_data