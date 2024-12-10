# schema_extractor/sanitizer.py

import os
import io
import pandas as pd
import numpy as np
import streamlit as st
import chardet
import tempfile
import re
from . import utils

def sanitize_files(uploaded_files):
    """
    Sanitizes the content of uploaded files.

    Args:
        uploaded_files (list): List of uploaded file objects.

    Returns:
        dict: A dictionary containing sanitized data for each file.
    """
    sanitized_data = {}
    for file in uploaded_files:
        st.write(f"Processing file: {file.name}")
        # Process each file
        sanitized_content = sanitize_file_content(file)
        if sanitized_content is not None:
            sanitized_data[file.name] = sanitized_content
    return sanitized_data

def sanitize_file_content(file):
    """
    Sanitizes the content of a single file.

    Performs checks for malformed data, harmful characters, duplicates,
    and sensitive information.

    Args:
        file (UploadedFile): The uploaded file object.

    Returns:
        any: Sanitized content of the file, or None if the user chooses to discard it.
    """
    # Step 1: Back up the data
    backup_path = utils.backup_data(file)

    # Step 2: Detect file type
    file_type = utils.detect_file_type(file)

    # Step 3: Read the file content based on file type
    if file_type in ['csv', 'tsv', 'xlsx', 'parquet', 'feather', 'hdf5']:
        df = read_tabular_file(file, file_type)
        if df is None:
            st.error(f"Failed to read file {file.name}.")
            return None

        # Step 4: Detect and handle malformed data
        df = detect_and_handle_malformed_data(df)

        # Step 5: Remove harmful characters
        df = remove_harmful_characters(df)

        # Step 6: Detect and redact sensitive data
        df = detect_and_redact_sensitive_data(df)

        # Step 7: Normalize formats and unify encodings
        df = normalize_formats_and_encodings(df)

        # Step 8: Detect and handle duplicates
        df = detect_and_handle_duplicates(df)

        # Step 9: Remove stopwords
        df = remove_stopwords_from_dataframe(df)

        # Step 10: Detect and handle unwanted content
        df = detect_and_handle_unwanted_content(df)

        # Step 11: Save sanitized data
        save_sanitized_data(df, file.name)

        return df

    elif file_type in ['json', 'xml', 'yaml', 'pickle', 'msgpack', 'bson', 'proto', 'avro']:
        # Process serialized data files
        st.error(f"Processing for {file_type} files is not yet implemented.")
        return None

    elif file_type in ['txt', 'doc', 'docx', 'pdf', 'md', 'log', 'rtf']:
        # Process unstructured text files
        text = read_text_file(file, file_type)

        # Step 4: Remove harmful characters
        text = remove_harmful_characters_text(text)

        # Step 5: Detect and redact sensitive data
        text = detect_and_redact_sensitive_data_text(text)

        # Step 6: Normalize text, unify encodings
        text = normalize_text(text)

        # Step 7: Remove stopwords
        text = remove_stopwords_from_text(text)

        # Step 8: Detect and handle unwanted content
        text = detect_and_handle_unwanted_content_text(text)

        # Step 9: Save sanitized data
        save_sanitized_text_data(text, file.name)

        return text

    else:
        st.error(f"Unsupported file type for file {file.name}.")
        return None

def read_tabular_file(file, file_type):
    """
    Reads a tabular file into a pandas DataFrame.

    Args:
        file (UploadedFile): The uploaded file object.
        file_type (str): The detected file type.

    Returns:
        pd.DataFrame or None: The DataFrame containing the file data, or None if reading fails.
    """
    try:
        if file_type == 'csv':
            df = pd.read_csv(file)
        elif file_type == 'tsv':
            df = pd.read_csv(file, sep='\t')
        elif file_type == 'xlsx':
            df = pd.read_excel(file)
        elif file_type == 'parquet':
            df = pd.read_parquet(file)
        elif file_type == 'feather':
            df = pd.read_feather(file)
        elif file_type == 'hdf5':
            df = pd.read_hdf(file)
        else:
            st.error(f"Unsupported tabular file type: {file_type}")
            return None
        return df
    except Exception as e:
        st.error(f"Error reading {file.name}: {e}")
        return None

def detect_and_handle_malformed_data(df):
    """
    Detects and handles malformed data in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        pd.DataFrame: The DataFrame with malformed data handled.
    """
    # Detect rows with missing values
    malformed = df.isnull().any(axis=1)
    num_malformed = malformed.sum()
    if num_malformed > 0:
        st.warning(f"Detected {num_malformed} malformed rows.")
        action = st.selectbox(f"What would you like to do with the malformed data?",
                              options=["Discard", "Fix (Fill NaNs)", "Keep as is"], key=f"malformed_{df.shape}")
        if action == "Discard":
            df = df.dropna()
            st.info(f"Discarded {num_malformed} malformed rows.")
        elif action == "Fix (Fill NaNs)":
            df = df.fillna(method='ffill').fillna(method='bfill')  # Forward and backward fill
            st.info(f"Filled missing values in {num_malformed} rows.")
        else:
            st.info(f"Keeping malformed data as is.")
    else:
        st.success("No malformed data detected.")
    return df

def remove_harmful_characters(df):
    """
    Removes harmful characters from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: The DataFrame with harmful characters removed.
    """
    # Define a pattern to match harmful characters
    harmful_chars_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).apply(lambda x: harmful_chars_pattern.sub('', x))
    st.success("Removed harmful characters from text data.")
    return df

def detect_and_redact_sensitive_data(df):
    """
    Detects and redacts sensitive data in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: The DataFrame with sensitive data redacted.
    """
    # Patterns for sensitive data
    sensitive_patterns = {
        'Email': r'[\w\.-]+@[\w\.-]+',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'Credit Card': r'\b(?:\d[ -]*?){13,16}\b',
        # Add more patterns as needed
    }
    sensitive_found = {}
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        for label, pattern in sensitive_patterns.items():
            matches = df[col].str.contains(pattern, regex=True, na=False)
            if matches.any():
                num_matches = matches.sum()
                sensitive_found.setdefault(col, []).append((label, num_matches))
                # Redact the data
                df.loc[matches, col] = df.loc[matches, col].str.replace(pattern, '[REDACTED]', regex=True)
    if sensitive_found:
        for col, findings in sensitive_found.items():
            for label, num in findings:
                st.warning(f"Found {num} instances of {label} in column '{col}'. Data has been redacted.")
    else:
        st.success("No sensitive data detected.")
    return df

def normalize_formats_and_encodings(df):
    """
    Normalizes formats and unifies data encodings in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: The DataFrame with normalized formats.
    """
    # Normalize date formats
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col])
        elif pd.api.types.is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], errors='raise')
            except (ValueError, TypeError):
                pass  # Not able to convert, keep as is
    # Normalize numeric formats
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    st.success("Normalized data formats and encodings.")
    return df

def detect_and_handle_duplicates(df):
    """
    Detects duplicated records and handles them as per user choice.

    Args:
        df (pd.DataFrame): The DataFrame to check for duplicates.

    Returns:
        pd.DataFrame: The DataFrame with duplicates handled.
    """
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        st.warning(f"Detected {num_duplicates} duplicated records.")
        action = st.selectbox(f"What would you like to do with the duplicated records?",
                              options=["Remove duplicates", "Keep as is"], key=f"duplicates_{df.shape}")
        if action == "Remove duplicates":
            df = df.drop_duplicates()
            st.info(f"Removed {num_duplicates} duplicated records.")
        else:
            st.info("Keeping duplicated records as is.")
    else:
        st.success("No duplicated records detected.")
    return df

def remove_stopwords_from_dataframe(df):
    """
    Removes stopwords from text columns in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: The DataFrame with stopwords removed from text columns.
    """
    # Get stopwords from user
    user_input = st.text_input("Enter stopwords to remove (comma-separated):", value="", key=f"stopwords_{df.shape}")
    stopwords = [word.strip().lower() for word in user_input.split(',') if word.strip()]
    if stopwords:
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).apply(
                lambda x: ' '.join([word for word in x.split() if word.lower() not in stopwords])
            )
        st.success("Removed stopwords from text columns.")
    else:
        st.info("No stopwords provided.")
    return df

def detect_and_handle_unwanted_content(df):
    """
    Detects harmful or unwanted content in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: The DataFrame with unwanted content handled.
    """
    # Define patterns for harmful or unwanted content
    unwanted_patterns = {
        'Profanity': r'\b(badword1|badword2|badword3)\b',  # Replace with actual words
        # Add more patterns as needed
    }
    unwanted_found = {}
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        for label, pattern in unwanted_patterns.items():
            matches = df[col].str.contains(pattern, flags=re.IGNORECASE, regex=True, na=False)
            if matches.any():
                num_matches = matches.sum()
                unwanted_found.setdefault(col, []).append((label, num_matches))
    if unwanted_found:
        for col, findings in unwanted_found.items():
            for label, num in findings:
                st.warning(f"Found {num} instances of {label} in column '{col}'.")
        action = st.selectbox(f"What would you like to do with the unwanted content?",
                              options=["Remove rows containing unwanted content", "Keep as is"], key=f"unwanted_{df.shape}")
        if action == "Remove rows containing unwanted content":
            for col in unwanted_found.keys():
                for label, pattern in unwanted_patterns.items():
                    matches = df[col].str.contains(pattern, flags=re.IGNORECASE, regex=True, na=False)
                    df = df[~matches]
            st.info("Removed rows containing unwanted content.")
        else:
            st.info("Keeping unwanted content as is.")
    else:
        st.success("No harmful or unwanted content detected.")
    return df

def save_sanitized_data(df, filename):
    """
    Saves the sanitized DataFrame for downstream processing.

    Args:
        df (pd.DataFrame): The sanitized DataFrame.
        filename (str): Original filename.

    Returns:
        str: Path to the saved file.
    """
    sanitized_filename = f"sanitized_{filename}"
    # Save to a temporary directory
    temp_dir = tempfile.gettempdir()
    sanitized_filepath = os.path.join(temp_dir, sanitized_filename)
    df.to_csv(sanitized_filepath, index=False)
    st.success(f"Sanitized data saved as {sanitized_filepath}")
    return sanitized_filepath

def read_text_file(file, file_type):
    """
    Reads an unstructured text file.

    Args:
        file (UploadedFile): The uploaded file object.
        file_type (str): The detected file type.

    Returns:
        str: The text content of the file.
    """
    try:
        text = file.read().decode('utf-8', errors='replace')
        return text
    except Exception as e:
        st.error(f"Error reading {file.name}: {e}")
        return None

def remove_harmful_characters_text(text):
    """
    Removes harmful characters from text.

    Args:
        text (str): The text data to process.

    Returns:
        str: The text with harmful characters removed.
    """
    harmful_chars_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
    text = harmful_chars_pattern.sub('', text)
    st.success("Removed harmful characters from text.")
    return text

def detect_and_redact_sensitive_data_text(text):
    """
    Detects and redacts sensitive data in text.

    Args:
        text (str): The text data to process.

    Returns:
        str: The text with sensitive data redacted.
    """
    # Patterns for sensitive data
    sensitive_patterns = {
        'Email': r'[\w\.-]+@[\w\.-]+',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'Credit Card': r'\b(?:\d[ -]*?){13,16}\b',
        # Add more patterns as needed
    }
    sensitive_found = False
    for label, pattern in sensitive_patterns.items():
        matches = re.findall(pattern, text)
        num_matches = len(matches)
        if num_matches > 0:
            sensitive_found = True
            st.warning(f"Found {num_matches} instances of {label} in text. Data has been redacted.")
            text = re.sub(pattern, '[REDACTED]', text)
    if not sensitive_found:
        st.success("No sensitive data detected.")
    return text

def normalize_text(text):
    """
    Normalizes text by unifying encodings and removing excess whitespace.

    Args:
        text (str): The text data to process.

    Returns:
        str: The normalized text.
    """
    # Normalize whitespace
    text = ' '.join(text.split())
    st.success("Normalized text.")
    return text

def remove_stopwords_from_text(text):
    """
    Removes stopwords from text.

    Args:
        text (str): The text data to process.

    Returns:
        str: The text with stopwords removed.
    """
    # Get stopwords from user
    user_input = st.text_input("Enter stopwords to remove (comma-separated):", value="", key="stopwords_text")
    stopwords = [word.strip().lower() for word in user_input.split(',') if word.strip()]
    if stopwords:
        words = text.split()
        text = ' '.join([word for word in words if word.lower() not in stopwords])
        st.success("Removed stopwords from text.")
    else:
        st.info("No stopwords provided.")
    return text

def detect_and_handle_unwanted_content_text(text):
    """
    Detects harmful or unwanted content in text.

    Args:
        text (str): The text data to process.

    Returns:
        str: The text with unwanted content handled.
    """
    # Define patterns for unwanted content
    unwanted_patterns = {
        'Profanity': r'\b(badword1|badword2|badword3)\b',  # Replace with actual words
        # Add more patterns as needed
    }
    unwanted_found = False
    for label, pattern in unwanted_patterns.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        num_matches = len(matches)
        if num_matches > 0:
            unwanted_found = True
            st.warning(f"Found {num_matches} instances of {label} in text.")
    if unwanted_found:
        action = st.selectbox(f"What would you like to do with the unwanted content?",
                              options=["Remove unwanted content", "Keep as is"], key="unwanted_text")
        if action == "Remove unwanted content":
            for label, pattern in unwanted_patterns.items():
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            st.info("Removed unwanted content from text.")
        else:
            st.info("Keeping unwanted content as is.")
    else:
        st.success("No harmful or unwanted content detected.")
    return text

def save_sanitized_text_data(text, filename):
    """
    Saves the sanitized text data for downstream processing.

    Args:
        text (str): The sanitized text data.
        filename (str): Original filename.

    Returns:
        str: Path to the saved file.
    """
    sanitized_filename = f"sanitized_{filename}"
    # Save to a temporary directory
    temp_dir = tempfile.gettempdir()
    sanitized_filepath = os.path.join(temp_dir, sanitized_filename)
    with open(sanitized_filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    st.success(f"Sanitized text saved as {sanitized_filepath}")
    return sanitized_filepath