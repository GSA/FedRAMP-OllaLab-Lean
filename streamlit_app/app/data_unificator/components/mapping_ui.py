# components/mapping_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_mapping import DataMapper
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.mapping_utils import verify_data_types
import traceback

logger = get_logger(__name__)

@st.fragment
def render_mapping():
    st.header("Data Mapping")
    st.write("Map fields across data sources and resolve conflicts.")

    # Placeholder for dynamic content
    content_placeholder = st.empty()

    try:
        # Assume data_sources is a list of imported data from previous step
        data_sources = st.session_state.get('imported_data', [])
        if not data_sources:
            st.warning("No data sources found. Please complete the Data Import step first.")
            st.stop()

        data_mapper = DataMapper(data_sources)

        # Step 1: Extract Fields
        if st.button("Extract Fields and Metadata"):
            data_mapper.extract_fields()
            st.success("Fields and metadata extracted.")
            record_action("User extracted fields and metadata.")

        # Step 2: Identify Overlapping Fields
        overlaps = data_mapper.identify_overlapping_fields()
        if overlaps:
            st.write("Overlapping Fields Identified:")
            for overlap in overlaps:
                st.write(f"Fields: {overlap['fields']}, Similarity: {overlap['similarity']:.2f}")
            record_action("User viewed overlapping fields.")
        else:
            st.info("No overlapping fields found.")

        # Step 3: Establish Source Hierarchy and Weights
        st.subheader("Source Hierarchy and Weights")
        source_files = [source['file'] for source in data_sources]
        default_weights = {file: 5 for file in source_files}
        source_hierarchy = st.multiselect(
            "Establish Source Hierarchy (top is highest priority)",
            options=source_files,
            default=source_files,
            format_func=lambda x: f"{x}"
        )
        st.write("Adjust Source Weights (higher means more reliable)")
        for file in source_files:
            default_weights[file] = st.slider(f"Weight for {file}", 1, 10, 5)

        data_mapper.source_hierarchy = source_hierarchy
        data_mapper.source_weights = default_weights
        record_action("User established source hierarchy and weights.")

        # Step 4: Align Data Structures
        if st.button("Align Data Structures"):
            data_mapper.align_structures()
            st.success("Data structures aligned.")
            record_action("User aligned data structures.")

        # Step 5: Detect and Resolve Conflicts
        st.subheader("Conflict Resolution Strategies")
        conflict_strategies = ["Manual", "Time-based", "Hierarchy-based", "Weight-based"]
        selected_strategy = st.selectbox("Select Conflict Resolution Strategy", conflict_strategies)
        if selected_strategy == "Manual":
            st.info("Manual conflict resolution will require user input for each conflict.")
        # Additional UI for strategy parameters can be added here

        if st.button("Detect and Resolve Conflicts"):
            data_mapper.detect_and_resolve_conflicts(selected_strategy)
            st.success("Conflicts resolved using selected strategy.")
            record_action(f"User resolved conflicts using {selected_strategy} strategy.")

        # Step 6: Create Mapping Dictionary
        st.subheader("Field Mapping")
        if st.button("Create Mapping Dictionary"):
            # Allow user to map fields via GUI
            for overlap in data_mapper.overlaps:
                st.write(f"Map fields for overlap: {overlap['fields']}")
                standard_name = st.text_input(f"Standard name for fields {overlap['fields']}", value=overlap['fields'][0])
                data_mapper.mapping_dictionary[standard_name] = overlap['fields']
            st.success("Mapping dictionary created.")
            record_action("User created mapping dictionary.")

        # Step 7: Save Mapping Dictionary
        if st.button("Save Mapping Dictionary"):
            data_mapper.save_mapping()
            st.success("Mapping dictionary saved.")
            record_action("User saved mapping dictionary.")

        # Step 8: Verify and Convert Data Types
        st.subheader("Data Type Verification and Conversion")
        incompatibilities = verify_data_types(data_mapper.resolved_data)
        if incompatibilities:
            st.warning("Data type incompatibilities found:")
            st.write(incompatibilities)
            # Allow user to select conversions
            user_conversions = {}
            for field, types in incompatibilities.items():
                st.write(f"Field '{field}' has incompatible types: {types}")
                selected_type = st.selectbox(f"Convert '{field}' to type:", options=['int', 'float', 'str', 'datetime'])
                user_conversions[field] = selected_type
            if st.button("Convert Data Types"):
                data_mapper.verify_and_convert_data_types(user_conversions)
                st.success("Data types converted.")
                record_action("User converted data types.")
        else:
            st.info("No data type incompatibilities found.")

    except Exception as e:
        logger.error(f"Error in Data Mapping: {str(e)}", exc_info=True)
        st.error("An error occurred during data mapping. Please check the logs for details.")
        st.exception(e)
        st.stop()
