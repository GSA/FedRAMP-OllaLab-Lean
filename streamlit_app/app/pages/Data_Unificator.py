app_version = "0.1"
app_title = "OllaLab - Data Unificator"
app_description = "Unify datasets stored in a local folder."
app_icon = ":open_file_folder:"

import streamlit as st
from streamlit.logger import get_logger
import multiprocessing
import logging
import sys
from data_unificator.components import import_ui, mapping_ui, normalization_ui, deduplication_ui, validation_ui
from modules import audit_trail

# Configure logging
logger = get_logger(__name__)
logging.basicConfig(
    filename='logs/data_unificator_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Implement global exception handling
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow user to interrupt the program
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    st.error("An unexpected error occurred. Please check the logs for more details.")
    st.exception(exc_value)
    st.stop()

sys.excepthook = handle_uncaught_exception

# Main application
def main():
    st.set_page_config(page_title="Data Unificator", layout="wide")

    st.title("Data Unificator Application")
    st.write("Welcome to the Data Unificator. Please follow the steps below to unify your data.")

    # Using st.empty() for dynamic content including error messages
    content_placeholder = st.empty()
    error_placeholder = st.empty()

    # Sidebar for navigation and settings
    st.sidebar.title("Navigation")
    steps = [
        "Data Import",
        "Data Mapping",
        "Data Normalization",
        "Data Deduplication",
        "Data Validation and Export"
    ]
    step = st.sidebar.radio("Select Step", steps)

    st.sidebar.title("Settings")
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
