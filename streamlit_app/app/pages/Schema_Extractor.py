# Schema_Extractor.py

app_version = "0.1"
app_title = "OllaLab - Schema Extractor"
app_description = "Schema and Structured Data Extractor from any data source."
app_icon = ":arrow_upper_right:"

import streamlit as st
from schema_extractor import file_uploader
from schema_extractor import sanitizer
from schema_extractor import tabular_data_processor
from schema_extractor import serialized_data_processor
from schema_extractor import unstructured_data_processor

def run_schema_extractor():
    """
    Runs the Schema Extractor application page.

    Handles user interactions, file uploads, processing options, and displays results.
    """
    st.title("Data Schema Extractor")
    st.write("Schema and Structured Data Extractor from any data source.")

    # Step 1: File Upload and Type Detection
    # Use the file_uploader module to handle file uploads and detect file type categories
    uploaded_files, file_type_category = file_uploader.upload_files()

    # Check if files are uploaded and a file type category is detected
    if uploaded_files is not None and file_type_category is not None:
        # Step 2: Sanitize Files
        # Use the sanitizer module to sanitize uploaded files
        sanitized_data = sanitizer.sanitize_files(uploaded_files)

        # Step 3: Inform User of Detected File Type Category
        st.write(f"Detected file type category: **{file_type_category.capitalize()}**")

        # Step 4: Process Data Based on File Type Category
        if file_type_category == 'serialized':
            st.header("Processing Serialized Data")
            # Process serialized data using the serialized_data_processor module
            serialized_data_processor.process_serialized_data(sanitized_data)
        elif file_type_category == 'tabular':
            st.header("Processing Tabular Data")
            # Process tabular data using the tabular_data_processor module
            tabular_data_processor.process_tabular_data(sanitized_data)
        elif file_type_category == 'unstructured':
            st.header("Processing Unstructured Data")
            # Process unstructured data using the unstructured_data_processor module
            unstructured_data_processor.process_unstructured_data(sanitized_data)
        else:
            # If file type category is unknown or unsupported, display an error
            st.error(f"Unsupported file type category: {file_type_category}")
    else:
        # If no files are uploaded, prompt the user to upload files
        st.info("Please upload files to proceed.")

if __name__ == "__main__":
    run_schema_extractor()