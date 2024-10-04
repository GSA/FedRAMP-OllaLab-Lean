# components/import_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_import import import_files_parallel, apply_missing_data_strategy
from data_unificator.utils.file_utils import get_supported_files
from data_unificator.audits.audit_trail import record_action
import os
import shutil
import pandas as pd

logger = get_logger(__name__)

@st.fragment
def render_import(num_workers):
    st.header("Data Import")
    st.write("Please select the folder containing your data files.")

    # Initialize session state variables
    if 'results' not in st.session_state:
        st.session_state['results'] = []
    if 'missing_data_strategies' not in st.session_state:
        st.session_state['missing_data_strategies'] = {}
    if 'data_imported' not in st.session_state:
        st.session_state['data_imported'] = False
    if 'manual_inputs' not in st.session_state:
        st.session_state['manual_inputs'] = {}

    folder = st.text_input("Folder Path", "app_data/data_unificator")
    start_import = st.button("Start Import")

    if start_import or st.session_state['data_imported']:
        if not os.path.isdir(folder):
            st.error("Invalid folder path. Please enter a valid directory.")
            return

        # Get list of supported files, excluding backup folder
        file_paths = get_supported_files(folder, exclude_backup=True)
        if not file_paths:
            st.warning("No supported data files found in the selected folder.")
            return

        st.write(f"Found {len(file_paths)} files to import.")

        # Record action
        if not st.session_state['data_imported']:
            record_action(f"Data Import - {len(file_paths)} files from '{folder}'")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                results = []
                for i, result in enumerate(import_files_parallel(file_paths, num_workers)):
                    progress = (i + 1) / len(file_paths)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {i + 1} of {len(file_paths)}")

                    results.append(result)

                st.session_state['results'] = results
                st.session_state['data_imported'] = True

            except Exception as e:
                logger.error(f"Data Import - {str(e)}", exc_info=True)
                st.error("An error occurred during import. Please check the logs for details.")
                st.exception(e)
                st.stop()
            finally:
                progress_bar.empty()
                status_text.empty()
        else:
            results = st.session_state['results']

        missing_data_strategies = st.session_state['missing_data_strategies']
        manual_inputs = st.session_state['manual_inputs']
        all_files_handled = True

        for result in results:
            file_name = result['file']

            if result['status'] == 'missing_data':
                st.warning(f"Missing data in '{file_name}'")
                missing_data_info = result['missing_data_info']
                df = result['data']

                col1,col2 = st.columns(2)

                for field, count in missing_data_info.items():
                    exist_count = df[field].count()
                    field_type = df[field].dtype
                    #strategies = ["Statistical Imputation", "Predictive Model", "Deletion", "Manual Input"]

                    if pd.api.types.is_numeric_dtype(df[field]):
                        available_strategies = ["Statistical Imputation", "Predictive Model", "Deletion", "Manual Input"]
                    else:
                        available_strategies = ["Deletion", "Manual Input"]

                    # Display the data
                    with col1:
                        st.write(f"**The field of {field}**")
                        st.write(f"Type: {field_type}")
                        st.write(f"Missing value ratio: {count}/{count+exist_count}")
                    with col2:
                        selected_strategy = st.selectbox(
                            label=f"Remediation strategy for '{field}'",
                            options=available_strategies,
                            key=f"strategy_{file_name}_{field}"
                        )

                        # Store strategy for the field
                        st.session_state['missing_data_strategies'][f"{file_name}_{field}"] = selected_strategy

                        # Allow manual input if selected
                        if selected_strategy == "Manual Input":
                            manual_value = st.text_input(
                                label=f"Input value for missing values in '{field}'",
                                key=f"manual_input_{file_name}_{field}"
                            )
                            st.session_state['manual_inputs'][f"{file_name}_{field}"] = manual_value

                st.session_state['manual_inputs'] = manual_inputs
                missing_data_strategies = st.session_state['missing_data_strategies']

            elif result['status'] == 'success':
                st.success(f"Successfully imported '{file_name}'")
                # Display EDA report
                with st.expander(f"EDA Report for '{os.path.basename(file_name)}'"):
                    st.write(result['eda_report'])
                # Display data hierarchy visualization
                st.image(f"{file_name}_hierarchy.png",caption=f"{file_name} Data Hierarchy")
            elif result['status'] == 'discrepancy':
                st.warning(f"Discrepancies found in '{file_name}'")
                st.write(result['discrepancies'])
            elif result['status'] == 'pii_found':
                st.warning(f"PII data found in '{file_name}'")
                st.write(f"PII Fields: {result['pii_fields']}")
            elif result['status'] == 'error':
                st.error(f"Error importing '{file_name}': {result['error']}")

        if st.button("Fix Missing Data") and missing_data_strategies:
            for result in results:
                file_name = result['file']
                backup_folder = os.path.join(folder, "backup")
                os.makedirs(backup_folder, exist_ok=True)
                original_file_path = [fp for fp in file_paths if os.path.basename(fp) == file_name][0]
                backup_file_path = os.path.join(backup_folder, os.path.basename(original_file_path))
                shutil.copy2(original_file_path, backup_file_path)
                st.info(f"Backed up '{file_name}' to '{backup_file_path}'")

                success = apply_missing_data_strategy(
                    original_file_path, st.session_state['missing_data_strategies'], st.session_state['manual_inputs']
                )
                if success:
                    st.success(f"Fixed missing data in '{file_name}'")
                    record_action(f"Applied missing data strategy to '{file_name}'")
                else:
                    st.error(f"Failed to fix missing data in '{file_name}'")

        if results:
            st.success("Data import completed.")
            record_action("Data import completed successfully.")
            st.session_state['imported_data'] = results
        else:
            st.warning("No data was imported.")
