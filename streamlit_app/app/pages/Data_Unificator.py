# Data_Unificator.py

app_version = "0.1"
app_title = "OllaLab - Data Unificator"
app_description = "Unify datasets stored in a local folder."
app_icon = ":open_file_folder:"

import streamlit as st
from streamlit.logger import get_logger
import multiprocessing
import logging
import sys

from data_unificator.config import ConfigManager
from data_unificator.utils.logging_utils import configure_logging

# Initialize ConfigManager
config_manager = ConfigManager()
# Configure logging using settings from ConfigManager
log_level = getattr(logging, config_manager.get('logging', 'log_level', 'INFO').upper(), logging.INFO)
log_file = config_manager.get('logging', 'log_file', 'logs/data_unificator_app.log')
configure_logging(log_level=log_level, log_file=log_file)

from data_unificator.components import import_ui, mapping_ui, normalization_ui, deduplication_ui, validation_ui
from data_unificator.audits import audit_trail
from data_unificator.utils.exception_utils import setup_global_exception_handler

# Set up global exception handler
setup_global_exception_handler()

# Define logger
logger = logging.getLogger(__name__)

# Main application
def main():
    st.set_page_config(page_title="Data Unificator", layout="wide")

    st.title("Data Unificator Application")
    st.write("Welcome to the Data Unificator. Please follow the steps below to unify your data.")

    # Using st.empty() for dynamic content including error messages
    content_placeholder = st.empty()
    error_placeholder = st.empty()

    # Sidebar for navigation and settings
    st.sidebar.markdown("## Data Unificator")
    steps = [
        "Data Import",
        "Data Mapping",
        "Data Normalization",
        "Data Deduplication",
        "Data Validation and Export"
    ]
    step = st.sidebar.radio("Select Step", steps)

    st.sidebar.markdown("## Settings")
    num_workers = st.sidebar.number_input(
        "Number of parallel processes",
        min_value=1,
        max_value=multiprocessing.cpu_count(),
        value=1
    )
    st.sidebar.write(f"CPU Cores Available: {multiprocessing.cpu_count()}")

    # Record user actions for audit trail
    audit_trail.record_action(f"Selected Step: {step}")
    audit_trail.record_action(f"Number of Workers: {num_workers}")

    # Main content based on selected step
    try:
        if step == "Data Import":
            with content_placeholder.container():
                import_ui.render_import(num_workers)
        elif step == "Data Mapping":
            with content_placeholder.container():
                mapping_ui.render_mapping()
        elif step == "Data Normalization":
            with content_placeholder.container():
                normalization_ui.render_normalization()
        elif step == "Data Deduplication":
            with content_placeholder.container():
                deduplication_ui.render_deduplication(num_workers)
        elif step == "Data Validation and Export":
            with content_placeholder.container():
                validation_ui.render_validation()
        else:
            st.error("Invalid selection.")
            logger.error(f"Invalid navigation step selected: {step}")
    except Exception as e:
        logger.error(f"Error in step '{step}': {str(e)}", exc_info=True)
        error_placeholder.error(f"An error occurred in step '{step}': {str(e)}")
        st.exception(e)
        st.stop()

if __name__ == "__main__":
    main()
