# components/normalization_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_normalization import DataNormalizer
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.normalization_utils import detect_outliers
import traceback

logger = get_logger(__name__)

@st.fragment
def render_normalization():
    st.header("Data Normalization")
    st.write("Standardize and normalize your data for consistency.")

    # Placeholder for dynamic content
    content_placeholder = st.empty()

    try:
        # Assume resolved_data is the output from the Data Mapping step
        resolved_data = st.session_state.get('resolved_data', [])
        if not resolved_data:
            st.warning("No data available for normalization. Please complete the previous steps.")
            st.stop()

        data_normalizer = DataNormalizer(resolved_data)

        # Step 1: Standardize Data Formats
        if st.button("Standardize Data Formats"):
            data_normalizer.standardize_data_formats()
            st.success("Data formats standardized.")
            record_action("User standardized data formats.")

        # Step 2: Handle Data Types
        if st.button("Handle Data Types"):
            data_normalizer.handle_data_types()
            st.success("Data types unified.")
            record_action("User handled data types.")

        # Step 3: Standardize Units of Measurement
        if st.button("Standardize Units of Measurement"):
            data_normalizer.standardize_units_of_measurement()
            st.success("Units of measurement standardized.")
            record_action("User standardized units of measurement.")

        # Step 4: Detect and Handle Outliers
        st.subheader("Outlier Detection and Handling")
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
        else:
            st.info("No significant outliers detected.")

        # Step 5: Apply Scaling to Fields
        st.subheader("Field Scaling")
        all_fields = data_normalizer.resolved_data[0]['data'].columns.tolist()
        fields_to_scale = st.multiselect("Select fields to scale", all_fields)
        scaling_methods = ["Min-Max Scaling (0-1)", "Z-score Normalization"]
        selected_scaling = st.selectbox("Select scaling method", scaling_methods)
        scaling_options = {'fields': fields_to_scale, 'method': selected_scaling}
        if st.button("Apply Scaling"):
            data_normalizer.apply_scaling_to_fields(scaling_options)
            st.success("Scaling applied to selected fields.")
            record_action(f"User applied {selected_scaling} to fields {fields_to_scale}.")

        # Step 6: Aggregate and Remove Fields
        st.subheader("Field Aggregation and Removal")
        # Aggregation
        aggregation_options = []
        st.write("Define new fields by aggregating existing fields:")
        num_aggregations = st.number_input("Number of new fields to create", min_value=0, max_value=10, value=0)
        for i in range(int(num_aggregations)):
            st.write(f"Aggregation {i+1}")
            new_field_name = st.text_input(f"New field name {i+1}")
            selected_fields = st.multiselect(f"Select fields to aggregate for {new_field_name}", all_fields)
            operation = st.selectbox(f"Select operation for {new_field_name}", ["Sum", "Average", "Max", "Min"])
            aggregation_options.append({
                'new_field': new_field_name,
                'fields': selected_fields,
                'operation': operation
            })
        # Removal
        fields_to_remove = st.multiselect("Select fields to remove", all_fields)
        if st.button("Apply Aggregation and Removal"):
            data_normalizer.aggregate_and_remove_fields(aggregation_options, fields_to_remove)
            st.success("Fields aggregated and/or removed.")
            record_action("User aggregated and removed fields.")

        # Step 7: Standardize Text Encoding
        if st.button("Standardize Text Encoding"):
            data_normalizer.standardize_text_encoding()
            st.success("Text encoding standardized.")
            record_action("User standardized text encoding.")

        # Display sample of normalized data
        st.subheader("Sample of Normalized Data")
        for data in data_normalizer.resolved_data:
            st.write(f"Data from '{data['file']}':")
            st.dataframe(data['data'].head())

    except Exception as e:
        logger.error(f"Error in Data Normalization: {str(e)}", exc_info=True)
        st.error("An error occurred during data normalization. Please check the logs for details.")
        st.exception(e)
        st.stop()
