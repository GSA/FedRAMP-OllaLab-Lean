# utils/exception_utils.py

import sys
import logging
import streamlit as st
from data_unificator.audits.audit_trail import record_action

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to catch any unhandled exceptions.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    record_action(f"Unhandled exception: {exc_value}")
    st.error("An unexpected error occurred. Please check the logs for more details.")
    st.exception(exc_value)
    st.stop()

def setup_global_exception_handler():
    """
    Set up the global exception handler.
    """
    sys.excepthook = handle_uncaught_exception
