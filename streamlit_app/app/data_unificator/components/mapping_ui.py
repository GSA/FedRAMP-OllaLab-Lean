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

    try:
        # Prepare data sources
        data_sources = prepare_data_sources()
        if not data_sources:
            st.warning("No valid imported data available for mapping")
            st.stop()

        data_mapper = DataMapper(data_sources)

        # Execute steps
        extract_fields_step(data_mapper)
        identify_overlapping_fields_step(data_mapper)
        create_mapping_dictionary_step(data_mapper)
        save_mapping_dictionary_step(data_mapper)
        establish_hierarchy_and_weights_step(data_mapper, data_sources)
        align_data_structures_step(data_mapper)
        detect_and_resolve_conflicts_step(data_mapper)
        verify_and_convert_data_types_step(data_mapper)

    except Exception as e:
        logger.error(f"Error in Data Mapping: {str(e)}", exc_info=True)
        st.error("An error occurred during data mapping. Please check the logs for details.")
        st.exception(e)
        st.stop()

def prepare_data_sources():
    # Assume data_sources is a list of imported data from previous step
    previous_results = st.session_state.get('results', [])
    if not previous_results:
        st.warning("No data sources found. Please complete the Data Import step first.")
        return None

    data_sources = []
    for result in previous_results:
        if result['status'] == 'success':
            # Only process successfully imported data
            file_name = result['file']
            data = result['data']
            file_extension = result['file_extension']
            hierarchy = st.session_state['hierarchy_data'].get(file_name, None)
            data_sources.append({
                'file': file_name,
                'data': data,
                'file_extension': file_extension,
                'hierarchy': hierarchy
            })
    return data_sources

@st.fragment
def extract_fields_step(data_mapper):
    # Step 1: Extract Fields
    if st.button("Extract Fields and Metadata"):
        data_mapper.extract_fields()
        st.success("Fields and metadata extracted.")

        # Display fields and metadata using Streamlit columns
        st.subheader("Fields and Metadata")
        for source_name, meta in data_mapper.field_metadata.items():
            st.write(f"### Source: {source_name}")
            metadata = meta['metadata']
            if metadata:
                # Display fields in columns
                field_items = list(metadata.items())
                num_fields = len(field_items)
                cols_per_row = 3  # Adjust number of columns per row as needed
                for i in range(0, num_fields, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for idx, (field_name, field_info) in enumerate(field_items[i:i+cols_per_row]):
                        with cols[idx]:
                            st.write(f"**Field:** {field_name}")
                            st.write(f"Data Type: {field_info['dtype']}")
                            st.write(f"Sample Values: {field_info['sample_values']}")
            else:
                st.write("No fields found in this source.")

@st.fragment
def identify_overlapping_fields_step(data_mapper):
    # Step 2: Identify Overlapping Fields
    overlaps = data_mapper.identify_overlapping_fields()
    if overlaps:
        st.write("### Overlapping Fields Identified:")
        confirmed_overlaps = []
        for overlap in overlaps:
            field_name = overlap['field_name']
            sources = overlap['sources']
            data_types = overlap['data_types']
            value_patterns = overlap['value_patterns']

            with st.expander(f"Field: {field_name}"):
                st.write(f"**Sources:** {', '.join(sources)}")
                st.write("**Data Types:**")
                for source_name in sources:
                    st.write(f"- {source_name}: {data_types[source_name]}")
                st.write("**Value Patterns:**")
                for source_name in sources:
                    st.write(f"- {source_name}: {value_patterns[source_name]}")
                # Ask user to confirm
                confirm = st.checkbox(f"Include '{field_name}' in mapping?", value=True, key=f"confirm_{field_name}")
                if confirm:
                    confirmed_overlaps.append(overlap)
        data_mapper.confirmed_overlaps = confirmed_overlaps
    else:
        st.info("No overlapping fields found.")

@st.fragment
def create_mapping_dictionary_step(data_mapper):
    # Step 3: Create Mapping Dictionary
    st.subheader("Field Mapping")
    if st.button("Create Mapping Dictionary"):
        if not hasattr(data_mapper, 'confirmed_overlaps') or not data_mapper.confirmed_overlaps:
            st.error("No confirmed overlaps to create mapping from. Please identify and confirm overlaps first.")
            return
        # Allow user to specify standard names and map source-specific field names
        for overlap in data_mapper.confirmed_overlaps:
            field_name = overlap['field_name']
            sources = overlap['sources']
            st.write(f"Map field '{field_name}' from sources: {', '.join(sources)}")
            standard_name = st.text_input(f"Standard name for field '{field_name}'", value=field_name, key=f"standard_{field_name}")
            if standard_name:
                # Map the source-specific field names to the standard name
                for source_name in sources:
                    if standard_name not in data_mapper.mapping_dictionary:
                        data_mapper.mapping_dictionary[standard_name] = []
                    data_mapper.mapping_dictionary[standard_name].append((source_name, field_name))
        st.success("Mapping dictionary created.")
        record_action("User created mapping dictionary.")

@st.fragment
def save_mapping_dictionary_step(data_mapper):
    # Step 4: Save Mapping Dictionary
    if st.button("Save Mapping Dictionary"):
        data_mapper.save_mapping()
        st.success("Mapping dictionary saved.")
        record_action("User saved mapping dictionary.")

@st.fragment
def establish_hierarchy_and_weights_step(data_mapper, data_sources):
    # Step 5: Establish Source Hierarchy and Weights
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

@st.fragment
def align_data_structures_step(data_mapper):
    # Step 6: Align Data Structures
    if st.button("Align Data Structures"):
        if not data_mapper.mapping_dictionary:
            st.error("Mapping dictionary is empty. Please create the mapping dictionary before aligning structures.")
            return
        data_mapper.align_structures()
        st.success("Data structures aligned.")
        record_action("User aligned data structures.")

@st.fragment
def detect_and_resolve_conflicts_step(data_mapper):
    # Step 7: Detect and Resolve Conflicts
    st.subheader("Conflict Resolution Strategies")
    conflict_strategies = ["Manual", "Time-based", "Hierarchy-based", "Weight-based"]
    selected_strategy = st.selectbox("Select Conflict Resolution Strategy", conflict_strategies)
    if selected_strategy == "Manual":
        st.info("Manual conflict resolution will require user input for each conflict.")
    # Additional UI for strategy parameters can be added here

    if st.button("Detect and Resolve Conflicts"):
        if not hasattr(data_mapper, 'aligned_data'):
            st.error("Data structures are not aligned yet. Please align data structures before resolving conflicts.")
        else:
            data_mapper.detect_and_resolve_conflicts(selected_strategy)
            st.success("Conflicts resolved using selected strategy.")
            record_action(f"User resolved conflicts using {selected_strategy} strategy.")

@st.fragment
def verify_and_convert_data_types_step(data_mapper):
    # Step 8: Verify and Convert Data Types
    st.subheader("Data Type Verification and Conversion")
    if hasattr(data_mapper, 'resolved_data'):
        incompatibilities = verify_data_types(data_mapper.resolved_data)
        if incompatibilities:
            st.warning("Data type incompatibilities found:")
            st.write(incompatibilities)
            # Allow user to select conversions
            user_conversions = {}
            for field, types in incompatibilities.items():
                st.write(f"Field '{field}' has incompatible types: {types}")
                selected_type = st.selectbox(f"Convert '{field}' to type:", options=['int', 'float', 'str', 'datetime'], key=f"convert_{field}")
                user_conversions[field] = selected_type
            if st.button("Convert Data Types"):
                data_mapper.verify_and_convert_data_types(user_conversions)
                st.success("Data types converted.")
                record_action("User converted data types.")
        else:
            st.info("No data type incompatibilities found.")
    else:
        st.info("Please resolve conflicts before verifying data types.")
