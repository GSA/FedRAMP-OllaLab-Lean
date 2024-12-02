# data_unificator/components/normalization_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_normalization import DataNormalizer
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.normalization_utils import detect_outliers
import pandas as pd  # Import pandas for type checking
import traceback

logger = get_logger(__name__)

def initialize_session_state():
    if 'resolved_data' not in st.session_state:
        st.session_state['resolved_data'] = None

@st.fragment
def render_normalization():
    st.header("Data Normalization")
    st.write("Standardize and normalize your data for consistency.")

    # Initialize session state
    initialize_session_state()

    # Placeholder for dynamic content
    content_placeholder = st.empty()

    try:
        # **Retrieve resolved_data from session_state**
        resolved_data = st.session_state.get('resolved_data', None)
        
        # **Check if resolved_data is available and in the correct format**
        if resolved_data is None:
            st.warning("No data available for normalization. Please complete the Data Mapping step first.")
            st.stop()
        
        # If resolved_data is a DataFrame, wrap it in a list for consistency
        if isinstance(resolved_data, pd.DataFrame):
            resolved_data = [{'file': 'Unnamed Source', 'data': resolved_data}]
            st.session_state['resolved_data'] = resolved_data  # Update session_state

        # If resolved_data is a list, ensure it's not empty
        elif isinstance(resolved_data, list):
            if len(resolved_data) == 0:
                st.warning("No data available for normalization. Please complete the Data Mapping step first.")
                st.stop()
            # Further check if each item is a dictionary with 'file' and 'data' keys
            for item in resolved_data:
                if not isinstance(item, dict) or 'file' not in item or 'data' not in item:
                    st.warning("Invalid data format in resolved_data. Please ensure it's a list of dictionaries with 'file' and 'data' keys.")
                    st.stop()
        else:
            st.warning("Invalid data format for normalization. Please ensure resolved_data is a list of dictionaries or a DataFrame.")
            st.stop()

        data_normalizer = DataNormalizer(resolved_data)

        # Render each normalization step
        standardize_data_formats()
        handle_data_types()
        standardize_units_of_measurement()
        detect_and_handle_outliers_step(data_normalizer)
        apply_scaling_to_fields_step(data_normalizer)
        aggregate_and_remove_fields_step(data_normalizer)
        standardize_text_encoding()
        display_normalized_data(data_normalizer)

    except Exception as e:
        logger.error(f"Error in Data Normalization: {str(e)}", exc_info=True)
        st.error("An error occurred during data normalization. Please check the logs for details.")
        st.exception(e)
        st.stop()

@st.fragment
def standardize_data_formats():
    if st.button("Standardize Data Formats"):
        try:
            data_normalizer = DataNormalizer(st.session_state['resolved_data'])
            data_normalizer.standardize_data_formats()
            st.success("Data formats standardized.")
            record_action("User standardized data formats.")
            st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
        except Exception as e:
            logger.error(f"Error in standardizing data formats: {str(e)}", exc_info=True)
            st.error("Failed to standardize data formats.")
            st.exception(e)

@st.fragment
def handle_data_types():
    if st.button("Handle Data Types"):
        try:
            data_normalizer = DataNormalizer(st.session_state['resolved_data'])
            data_normalizer.handle_data_types()
            st.success("Data types unified.")
            record_action("User handled data types.")
            st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
        except Exception as e:
            logger.error(f"Error in handling data types: {str(e)}", exc_info=True)
            st.error("Failed to handle data types.")
            st.exception(e)

@st.fragment
def standardize_units_of_measurement():
    if st.button("Standardize Units of Measurement"):
        try:
            data_normalizer = DataNormalizer(st.session_state['resolved_data'])
            data_normalizer.standardize_units_of_measurement()
            st.success("Units of measurement standardized.")
            record_action("User standardized units of measurement.")
            st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
        except Exception as e:
            logger.error(f"Error in standardizing units: {str(e)}", exc_info=True)
            st.error("Failed to standardize units of measurement.")
            st.exception(e)

@st.fragment
def detect_and_handle_outliers_step(data_normalizer: DataNormalizer):
    st.subheader("Outlier Detection and Handling")
    try:
        outlier_info = detect_outliers(data_normalizer.resolved_data)
        if outlier_info:
            st.warning("Outliers detected in the data.")
            # Display outlier information
            for data in outlier_info:
                st.write(f"Outliers in '{data['file']}':")
                st.write(data['outliers'])
            # Allow user to select action
            outlier_actions = ["Capping", "Removal", "Transformation", "Ignore"]
            selected_action = st.selectbox("Select action for outliers", outlier_actions)
            if st.button("Apply Outlier Handling"):
                data_normalizer.detect_and_handle_outliers(selected_action)
                st.success(f"Outliers handled using {selected_action}.")
                record_action(f"User handled outliers using {selected_action}.")
                st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
        else:
            st.info("No significant outliers detected.")
    except Exception as e:
        logger.error(f"Error in outlier detection/handling: {str(e)}", exc_info=True)
        st.error("An error occurred while detecting or handling outliers.")
        st.exception(e)

@st.fragment
def apply_scaling_to_fields_step(data_normalizer: DataNormalizer):
    st.subheader("Field Scaling")
    try:
        all_fields = []
        for data in data_normalizer.resolved_data:
            all_fields.extend(data['data'].columns.tolist())
        all_fields = list(set(all_fields))  # Remove duplicates

        fields_to_scale = st.multiselect("Select fields to scale", all_fields)
        scaling_methods = ["Min-Max Scaling (0-1)", "Z-score Normalization"]
        selected_scaling = st.selectbox("Select scaling method", scaling_methods)
        scaling_options = {'fields': fields_to_scale, 'method': selected_scaling}
        if st.button("Apply Scaling"):
            if not fields_to_scale:
                st.error("Please select at least one field to scale.")
            else:
                data_normalizer.apply_scaling_to_fields(scaling_options)
                st.success("Scaling applied to selected fields.")
                record_action(f"User applied {selected_scaling} to fields {fields_to_scale}.")
                st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
    except Exception as e:
        logger.error(f"Error in applying scaling: {str(e)}", exc_info=True)
        st.error("An error occurred while applying scaling to fields.")
        st.exception(e)

@st.fragment
def aggregate_and_remove_fields_step(data_normalizer: DataNormalizer):
    st.subheader("Field Aggregation and Removal")
    try:
        # Aggregation
        aggregation_options = []
        st.write("Define new fields by aggregating existing fields:")
        num_aggregations = st.number_input("Number of new fields to create", min_value=0, max_value=10, value=0, step=1)
        for i in range(int(num_aggregations)):
            st.write(f"Aggregation {i+1}")
            new_field_name = st.text_input(f"New field name {i+1}", key=f"agg_new_field_{i}")
            selected_fields = st.multiselect(f"Select fields to aggregate for {new_field_name}", 
                                             [field for data in data_normalizer.resolved_data for field in data['data'].columns], 
                                             key=f"agg_select_fields_{i}")
            operation = st.selectbox(f"Select operation for {new_field_name}", ["Sum", "Average", "Max", "Min"], key=f"agg_operation_{i}")
            aggregation_options.append({
                'new_field': new_field_name,
                'fields': selected_fields,
                'operation': operation
            })
        # Removal
        all_fields = []
        for data in data_normalizer.resolved_data:
            all_fields.extend(data['data'].columns.tolist())
        all_fields = list(set(all_fields))  # Remove duplicates
        fields_to_remove = st.multiselect("Select fields to remove", all_fields, key="fields_to_remove")
        if st.button("Apply Aggregation and Removal"):
            try:
                data_normalizer.aggregate_and_remove_fields(aggregation_options, fields_to_remove)
                st.success("Fields aggregated and/or removed.")
                record_action("User aggregated and removed fields.")
                st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
            except Exception as e:
                logger.error(f"Error during aggregation and removal: {str(e)}", exc_info=True)
                st.error("An error occurred while aggregating and removing fields. Please check the logs for details.")
                st.exception(e)
    except Exception as e:
        logger.error(f"Error in aggregation and removal step: {str(e)}", exc_info=True)
        st.error("An error occurred in the aggregation and removal step.")
        st.exception(e)

@st.fragment
def standardize_text_encoding():
    if st.button("Standardize Text Encoding"):
        try:
            data_normalizer = DataNormalizer(st.session_state['resolved_data'])
            data_normalizer.standardize_text_encoding()
            st.success("Text encoding standardized.")
            record_action("User standardized text encoding.")
            st.session_state['resolved_data'] = data_normalizer.resolved_data  # Update session_state
        except Exception as e:
            logger.error(f"Error in standardizing text encoding: {str(e)}", exc_info=True)
            st.error("Failed to standardize text encoding.")
            st.exception(e)

@st.fragment
def display_normalized_data(data_normalizer: DataNormalizer):
    st.subheader("Sample of Normalized Data")
    try:
        for data in data_normalizer.resolved_data:
            st.write(f"Data from '{data['file']}':")
            st.dataframe(data['data'].head())
    except Exception as e:
        logger.error(f"Error in displaying normalized data: {str(e)}", exc_info=True)
        st.error("Failed to display normalized data.")
        st.exception(e)
