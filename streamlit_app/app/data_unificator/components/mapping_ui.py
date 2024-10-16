# components/mapping_ui.py

import os
import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_mapping import DataMapper
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.mapping_utils import verify_data_types
import traceback

logger = get_logger(__name__)

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
        establish_hierarchy_step(data_mapper, data_sources)
        create_mapping_dictionary_step(data_mapper)
        save_mapping_dictionary_step(data_mapper)
        align_data_structures_step(data_mapper)
        save_temporary_merged_file_step(data_mapper)
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
            sample_values = overlap['sample_values']
            same_dtype = overlap['same_dtype']
            sample_similarity = overlap['sample_similarity']

            with st.expander(f"Field: {field_name}"):
                st.write(f"**Sources:** {', '.join(sources)}")
                st.write("**Data Types:**")
                for source_name in sources:
                    st.write(f"- {source_name}: {data_types[source_name]}")
                st.write(f"**Same Data Type:** {'Yes' if same_dtype else 'No'}")
                st.write("**Sample Values:**")
                for source_name in sources:
                    st.write(f"- {source_name}: {sample_values[source_name]}")
                st.write("**Sample Value Similarity:**")
                for (source_a, source_b), similarity in sample_similarity.items():
                    st.write(f"- {source_a} vs {source_b}: {similarity:.2f}")
                # Ask user to confirm
                confirm = st.checkbox(f"Include '{field_name}' in mapping?", value=True, key=f"confirm_{field_name}")
                if confirm:
                    confirmed_overlaps.append(overlap)
        data_mapper.confirmed_overlaps = confirmed_overlaps
    else:
        st.info("No overlapping fields found.")

def create_mapping_dictionary_step(data_mapper):
    # Step 3: Create Mapping Dictionary
    st.subheader("Field Mapping")
    if st.button("Create Mapping Dictionary"):
        if not data_mapper.source_hierarchy:
            st.error("Source hierarchy is not established. Please establish source hierarchy first.")
            return

        # Initialize mapping dictionary
        data_mapper.mapping_dictionary = {}

        # Start mapping from the highest priority source
        for idx, source in enumerate(data_mapper.source_hierarchy):
            st.write(f"### Mapping fields for source '{source}' (Level {idx+1})")
            source_fields = list(data_mapper.field_metadata[source]['metadata'].keys())

            # For the highest priority source, use its fields as anchor fields
            if idx == 0:
                for field in source_fields:
                    data_mapper.mapping_dictionary[field] = [(source, field)]
                anchor_fields = list(data_mapper.mapping_dictionary.keys())
                st.write(f"Anchor fields from '{source}': {anchor_fields}")
            else:
                # For lower priority sources, map their fields
                for field in source_fields:
                    st.write(f"Field '{field}' from source '{source}'")
                    # Options: map to anchor field, map to new field, leave as is
                    mapping_options = ['Map to anchor field', 'Map to new field', 'Leave as is']
                    selected_option = st.selectbox(
                        f"Select mapping option for field '{field}' from '{source}'",
                        mapping_options,
                        key=f"mapping_option_{source}_{field}"
                    )
                    if selected_option == 'Map to anchor field':
                        # User selects which anchor field to map to
                        selected_anchor_field = st.selectbox(
                            f"Select anchor field to map '{field}' to",
                            anchor_fields,
                            key=f"anchor_field_{source}_{field}"
                        )
                        data_mapper.mapping_dictionary[selected_anchor_field].append((source, field))
                    elif selected_option == 'Map to new field':
                        new_field_name = st.text_input(
                            f"Specify new field name for '{field}'",
                            key=f"new_field_{source}_{field}"
                        )
                        if new_field_name:
                            if new_field_name not in data_mapper.mapping_dictionary:
                                data_mapper.mapping_dictionary[new_field_name] = []
                            data_mapper.mapping_dictionary[new_field_name].append((source, field))
                    else:
                        # Leave as is
                        if field not in data_mapper.mapping_dictionary:
                            data_mapper.mapping_dictionary[field] = []
                        data_mapper.mapping_dictionary[field].append((source, field))
        st.success("Mapping dictionary created.")
        record_action("User created mapping dictionary.")

def save_mapping_dictionary_step(data_mapper):
    # Step 4: Save Mapping Dictionary
    if st.button("Save Mapping Dictionary"):
        data_mapper.save_mapping()
        st.success("Mapping dictionary saved.")
        record_action("User saved mapping dictionary.")

def establish_hierarchy_step(data_mapper, data_sources):
    # Step 5: Establish Source Hierarchy
    st.subheader("Source Hierarchy")
    source_files =  [source['file'] for source in data_sources]
    max_levels = len(source_files)
    num_levels = st.number_input(
        "Specify the number of source hierarchy levels:",
        min_value=1,
        max_value=max_levels,
        value=max_levels,
        step=1
    )
    selected_files = []
    source_hierarchy = []
    for level in range(1, num_levels + 1):
        remaining_files = [f for f in source_files if f not in selected_files]
        selected_file = st.selectbox(
            f"Select source file for level {level} (1 is highest priority):",
            options=remaining_files,
            key=f"hierarchy_level_{level}"
        )
        selected_files.append(selected_file)
        source_hierarchy.append(selected_file)
    data_mapper.source_hierarchy = source_hierarchy
    record_action("User established source hierarchy and weights.")

def align_data_structures_step(data_mapper):
    # Step 6: Align Data Structures
    if st.button("Align Data Structures"):
        if not data_mapper.mapping_dictionary:
            st.error("Mapping dictionary is empty. Please create the mapping dictionary before aligning structures.")
            return
        data_mapper.align_structures()
        st.success("Data structures aligned.")
        record_action("User aligned data structures.")

def save_temporary_merged_file_step(data_mapper):
    # New Step: Save Temporary Merged File
    st.subheader("Save Temporary Merged File")
    temp_file_name = st.text_input("Specify a file name for the temporary merged file:")
    if st.button("Merge and Save Temporary File"):
        if not data_mapper.mapping_dictionary:
            st.error("Mapping dictionary is empty. Please create the mapping dictionary before merging.")
            return
        if not temp_file_name:
            st.error("Please specify a valid file name.")
            return
        try:
            data_mapper.merge_data_sources()
            data_mapper.save_temporary_merged_file(temp_file_name)
            st.success(f"Temporary merged file saved as '{temp_file_name}'.")
            st.session_state['temp_merged_file'] = temp_file_name
            record_action(f"User saved temporary merged file '{temp_file_name}'.")
        except Exception as e:
            st.error(f"An error occurred during merging: {str(e)}")

def detect_and_resolve_conflicts_step(data_mapper):
    # Step 7: Detect and Resolve Conflicts
    if 'temp_merged_file' not in st.session_state:
        st.info("Please save a temporary merged file before detecting conflicts.")
        return

    st.subheader("Conflict Detection and Resolution")

    conflict_strategies = ["Manual", "Time-based", "Hierarchy-based", "Weight-based"]
    selected_strategy = st.selectbox("Select Conflict Resolution Strategy", conflict_strategies)

    if st.button("Detect Conflicts"):
        temp_file_name = st.session_state['temp_merged_file']
        try:
            data_mapper.load_temporary_merged_file(temp_file_name)
            data_mapper.detect_conflicts(report_row_numbers=True)
            if data_mapper.conflicts:
                st.write("### Conflicts Detected:")
                for keys, conflict in data_mapper.conflicts.items():
                    st.write(f"Conflict at keys: {keys}")
                    for field, details in conflict.items():
                        st.write(f"- Field: {field}")
                        for source, info in details.items():
                            st.write(f"  - Source: {source}")
                            st.write(f"    - Values: {info['values']}")
                            st.write(f"    - Rows: {info['rows']}")
                if selected_strategy == "Manual":
                    st.write("Manual conflict resolution:")
                    # Allow user to delete conflicting rows or edit values
                    for conflict_key, conflict_fields in data_mapper.conflicts.items():
                        st.write(f"Conflict at keys: {conflict_key}")
                        for field, field_conflict in conflict_fields.items():
                            st.write(f"Field: {field}")
                            # Display conflicting rows
                            conflicting_rows = data_mapper.get_conflicting_rows(conflict_key, field)
                            st.write(conflicting_rows)
                            # Allow user to edit or delete rows
                            action = st.selectbox(f"Action for conflict at {conflict_key} in field '{field}'",
                                                  options=['Keep First', 'Delete Rows', 'Edit Values'],
                                                  key=f"conflict_action_{conflict_key}_{field}")
                            if action == 'Delete Rows':
                                data_mapper.mark_rows_for_deletion(conflict_key, field)
                            elif action == 'Edit Values':
                                # Allow user to input new value
                                new_value = st.text_input(f"New value for field '{field}' at {conflict_key}",
                                                          key=f"edit_value_{conflict_key}_{field}")
                                data_mapper.update_conflict_value(conflict_key, field, new_value)
                else:
                    st.write(f"Conflicts will be resolved using the '{selected_strategy}' strategy.")
                st.session_state['conflict_strategy'] = selected_strategy
                st.session_state['conflicts_detected'] = True
            else:
                st.success("No conflicts detected.")
                st.session_state['conflicts_detected'] = False
        except Exception as e:
            st.error(f"An error occurred during conflict detection: {str(e)}")

    if st.session_state.get('conflicts_detected', False):
        if st.button("Resolve Conflicts"):
            try:
                temp_file_name = st.session_state['temp_merged_file']
                output_file_name = "fixed_conflicts_" + temp_file_name
                selected_strategy = st.session_state['conflict_strategy']
                data_mapper.resolve_conflicts(selected_strategy)
                data_mapper.save_resolved_data(output_file_name)
                st.success(f"Conflicts resolved and data saved to '{output_file_name}'.")
                record_action(f"User resolved conflicts and saved data to '{output_file_name}'.")
            except Exception as e:
                st.error(f"An error occurred during conflict resolution: {str(e)}")

def verify_and_convert_data_types_step(data_mapper):
    # Step 8: Verify and Convert Data Types
    st.subheader("Data Type Verification and Conversion")
    if hasattr(data_mapper, 'resolved_data'):
        incompatibilities = verify_data_types([{'data': data_mapper.resolved_data}])
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
