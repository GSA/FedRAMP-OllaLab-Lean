# components/import_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_import import import_files_parallel
from data_unificator.utils.file_utils import get_supported_files
from data_unificator.audits.audit_trail import record_action
import os

logger = get_logger(__name__)

@st.fragment
def render_import(num_workers):
    st.header("Data Import")
    st.write("Please select the folder containing your data files.")

    folder = st.text_input("Folder Path", "")
    start_import = st.button("Start Import")

    if start_import:
        if not os.path.isdir(folder):
            st.error("Invalid folder path. Please enter a valid directory.")
            return

        # Get list of supported files
        file_paths = get_supported_files(folder)
        if not file_paths:
            st.warning("No supported data files found in the selected folder.")
            return

        st.write(f"Found {len(file_paths)} files to import.")

        # Record action
        record_action(f"User initiated import for {len(file_paths)} files from '{folder}'")

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = []
        try:
            for i, result in enumerate(import_files_parallel(file_paths, num_workers)):
                progress = (i + 1) / len(file_paths)
                progress_bar.progress(progress)
                status_text.text(f"Processing file {i + 1} of {len(file_paths)}")

                # Handle result statuses
                if result['status'] == 'success':
                    st.success(f"Successfully imported '{result['file']}'")
                    # Display EDA report (collapsible)
                    with st.expander(f"EDA Report for '{os.path.basename(result['file'])}'"):
                        st.write(result['eda_report'])
                elif result['status'] == 'discrepancy':
                    st.warning(f"Discrepancies found in '{result['file']}'")
                    # Display discrepancies
                    st.write(result['discrepancies'])
                    # Offer options to user
                    if st.button(f"Accept discrepancies in '{result['file']}'"):
                        # Proceed despite discrepancies
                        results.append(result)
                    else:
                        st.stop()
                elif result['status'] == 'missing_data':
                    st.warning(f"Missing data in '{result['file']}'")
                    st.write(result['missing_data_info'])
                    # Allow user to select strategy
                    strategy = st.selectbox(
                        f"Select strategy for handling missing data in '{result['file']}'",
                        ["Statistical Imputation", "Predictive Model", "Deletion", "Manual Input"]
                    )
                    # Implement strategy (placeholder)
                    st.info(f"Selected strategy: {strategy}")
                    # Proceed after handling
                    results.append(result)
                elif result['status'] == 'pii_found':
                    st.warning(f"PII data found in '{result['file']}'")
                    st.write(f"PII Fields: {result['pii_fields']}")
                    # Allow user to take action
                    if st.button(f"Remove PII from '{result['file']}'"):
                        # Implement PII removal (placeholder)
                        st.info(f"PII removed from '{result['file']}'")
                        results.append(result)
                    else:
                        st.stop()
                elif result['status'] == 'error':
                    st.error(f"Error importing '{result['file']}': {result['error']}")
                else:
                    st.error(f"Unknown status for file '{result['file']}'")
        except Exception as e:
            logger.error(f"Error during import: {str(e)}", exc_info=True)
            st.error("An error occurred during import. Please check the logs for details.")
            st.exception(e)
            st.stop()

        progress_bar.empty()
        status_text.empty()

        if results:
            st.success("Data import completed.")
            # Proceed to next step or save results for later use
            record_action("Data import completed successfully.")
        else:
            st.warning("No data was imported.")
