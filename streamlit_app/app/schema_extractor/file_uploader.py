# schema_extractor/file_uploader.py

import streamlit as st
import os
from schema_extractor.utils import detect_file_category

def upload_files():
    """
    Handles file uploads and detects file type categories.

    Ensures that all uploaded files are of the same format and type category.

    Returns:
        tuple:
            - uploaded_files (List[UploadedFile]): A list of uploaded file objects.
            - file_type_category (str): The detected file type category ('tabular', 'serialized', 'unstructured').

    Raises:
        ValueError: If files of different type categories are uploaded or if unsupported file types are detected.
    """
    st.header("Upload Your Files")

    # Allowed file extensions
    allowed_extensions = [
        'csv', 'tsv', 'xlsx', 'parquet', 'json', 'xml', 'txt', 'pdf', 'md',
        'log', 'rtf', 'pickle', 'msgpack', 'bson', 'proto', 'avro', 'feather',
        'hdf5', 'yaml', 'doc', 'docx'
    ]

    # File uploader widget
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=allowed_extensions
    )

    if not uploaded_files:
        st.info("Please upload one or more files to proceed.")
        return None, None
    else:
        # List to store detected file type categories
        file_type_categories = []

        for uploaded_file in uploaded_files:
            try:
                # Detect the file type category using the utility function
                file_type_category = detect_file_category(uploaded_file)
                if file_type_category == 'unknown':
                    st.warning(f"File '{uploaded_file.name}' has an unsupported file type or cannot be processed.")
                    return None, None
                else:
                    file_type_categories.append(file_type_category)
            except Exception as e:
                st.error(f"An error occurred while processing file '{uploaded_file.name}': {e}")
                return None, None

        # Ensure all files are of the same type category
        if len(set(file_type_categories)) > 1:
            st.warning("All uploaded files must be of the same type category (e.g., all tabular files, or all serialized data files).")
            return None, None
        else:
            file_type_category = file_type_categories[0]
            st.success(f"{len(uploaded_files)} file(s) uploaded successfully.")
            st.write(f"Detected file type category: **{file_type_category}**")
            return uploaded_files, file_type_category