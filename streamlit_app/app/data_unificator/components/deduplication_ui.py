# components/deduplication_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_deduplication import DataDeduplicator
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.deduplication_utils import list_common_fields
import traceback

logger = get_logger(__name__)

@st.fragment
def render_deduplication(num_workers):
    st.header("Data Deduplication and Consolidation")
    st.write("Merge datasets and eliminate duplicates based on your criteria.")

    # Placeholder for dynamic content
    content_placeholder = st.empty()

    try:
        # Assume normalized_data is the output from the Data Normalization step
        normalized_data = st.session_state.get('normalized_data', [])
        if not normalized_data:
            st.warning("No data available for deduplication. Please complete the previous steps.")
            st.stop()

        data_deduplicator = DataDeduplicator(normalized_data)

        # Step 1: Merge Data
        if st.button("Merge Data"):
            data_deduplicator.merge_data()
            st.success("Data merged successfully.")
            record_action("User merged data.")
            # Display sample of consolidated data
            st.subheader("Sample of Consolidated Data")
            st.dataframe(data_deduplicator.consolidated_data.head())

        # Step 2: Configure Duplicate Detection Criteria
        st.subheader("Configure Duplicate Detection Criteria")
        common_fields = list_common_fields(normalized_data)
        criteria_options = [
            "Exact Match",
            "Fuzzy Match",
            "Composite Key Matching",
            "Custom Rules"
        ]
        selected_criteria = st.multiselect("Select Duplicate Detection Criteria", criteria_options)
        user_defined_fields = []
        if "Composite Key Matching" in selected_criteria or "Custom Rules" in selected_criteria:
            user_defined_fields = st.multiselect("Select Fields for Composite Key or Custom Rules", common_fields)
        # Additional parameters for fuzzy matching
        if "Fuzzy Match" in selected_criteria:
            similarity_threshold = st.slider("Set Similarity Threshold for Fuzzy Matching", 0.0, 1.0, 0.8)

        criteria_config = {
            "selected_criteria": selected_criteria,
            "user_defined_fields": user_defined_fields,
            "similarity_threshold": similarity_threshold if "Fuzzy Match" in selected_criteria else None
        }

        if st.button("Configure Duplicate Detection"):
            data_deduplicator.configure_duplicate_detection(criteria_config)
            st.success("Duplicate detection criteria configured.")
            record_action("User configured duplicate detection criteria.")

        # Step 3: Detect and Eliminate Duplicates
        if st.button("Detect and Eliminate Duplicates"):
            data_deduplicator.detect_and_eliminate_duplicates()
            st.success("Duplicates detected and eliminated.")
            record_action("User detected and eliminated duplicates.")
            # Display sample of deduplicated data
            st.subheader("Sample of Deduplicated Data")
            st.dataframe(data_deduplicator.consolidated_data.head())

        # Step 4: Save Consolidated Dataset
        st.subheader("Save Consolidated Dataset")
        output_path = st.text_input("Enter the output file path (e.g., 'output/consolidated_data.csv')", "output/consolidated_data.csv")
        if st.button("Save Consolidated Data"):
            data_deduplicator.save_consolidated_dataset(output_path)
            st.success(f"Consolidated data saved to '{output_path}'.")
            record_action(f"User saved consolidated data to '{output_path}'.")

    except Exception as e:
        logger.error(f"Error in Data Deduplication: {str(e)}", exc_info=True)
        st.error("An error occurred during data deduplication. Please check the logs for details.")
        st.exception(e)
        st.stop()
