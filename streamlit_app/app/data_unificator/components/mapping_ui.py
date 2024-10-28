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

    # Initialize necessary session_state variables
    if 'data_mapper' not in st.session_state:
        # Prepare data sources
        data_sources = prepare_data_sources()
        if not data_sources:
            st.warning("No valid imported data available for mapping")
            st.stop()
        # Initialize and store DataMapper in session_state
        st.session_state['data_mapper'] = DataMapper(data_sources)

    if 'confirmed_overlaps' not in st.session_state:
        st.session_state['confirmed_overlaps'] = []

    if 'selected_files' not in st.session_state:
        st.session_state['selected_files'] = []

    if 'source_hierarchy' not in st.session_state:
        st.session_state['source_hierarchy'] = []

    if 'anchor_fields' not in st.session_state:
        st.session_state['anchor_fields'] = []

    if 'user_conversions' not in st.session_state:
        st.session_state['user_conversions'] = {}

    if 'conflict_strategy' not in st.session_state:
        st.session_state['conflict_strategy'] = "Manual"

    if 'conflicts_detected' not in st.session_state:
        st.session_state['conflicts_detected'] = False

    if 'temp_merged_file' not in st.session_state:
        st.session_state['temp_merged_file'] = ''

    data_mapper = st.session_state['data_mapper']

    try:
        # Check if temp merged file exists and skip earlier steps if it does
        temp_file_path = st.session_state.get('temp_merged_file', '')
        if temp_file_path and os.path.exists(temp_file_path):
            st.success(f"Temporary merged file '{temp_file_path}' already exists.")
            # Load the temp merged file
            data_mapper.load_temporary_merged_file(temp_file_path)
            # Ensure resolved_data is set
            if not hasattr(data_mapper, 'resolved_data') or data_mapper.resolved_data is None:
                data_mapper.resolved_data = data_mapper.merged_data
                st.session_state['data_mapper'] = data_mapper
                # **Set resolved_data in session_state**
                st.session_state['resolved_data'] = data_mapper.resolved_data

            # Proceed to conflict detection and data type verification
            detect_and_resolve_conflicts_step(data_mapper)
        else:
            # Execute steps in order
            extract_fields_step(data_mapper)
            identify_overlapping_fields_step(data_mapper)
            establish_hierarchy_step(data_mapper)
            create_mapping_dictionary_step(data_mapper)
            save_mapping_dictionary_step(data_mapper)
            align_data_structures_step(data_mapper)
            save_temporary_merged_file_step(data_mapper)
            # After saving, automatically run conflict detection and data type verification
            if st.session_state.get('temp_merged_file', '') and os.path.exists(st.session_state['temp_merged_file']):
                detect_and_resolve_conflicts_step(data_mapper)

    except Exception as e:
        logger.error(f"Error in Data Mapping: {str(e)}", exc_info=True)
        st.error("An error occurred during data mapping. Please check the logs for details.")
        st.exception(e)
        st.stop()

def prepare_data_sources():
    """
    Prepare data sources from the previous import step.
    """
    previous_results = st.session_state.get('results', [])
    if not previous_results:
        st.warning("No data sources found. Please complete the Data Import step first.")
        return None

    data_sources = []
    hierarchy_data = st.session_state.get('hierarchy_data', {})
    for result in previous_results:
        if result.get('status') == 'success':
            # Only process successfully imported data
            file_name = os.path.basename(result['file'])
            file_path = result['file']  # Full file path
            data = result['data']
            file_extension = result.get('file_extension', '')
            hierarchy = hierarchy_data.get(file_name, None)
            data_sources.append({
                'file': file_name,         # Base file name for keys and display
                'file_path': file_path,    # Full path for file operations
                'data': data,
                'file_extension': file_extension,
                'hierarchy': hierarchy
            })
    return data_sources

@st.fragment
def extract_fields_step(data_mapper):
    """
    Step 1: Extract Fields and Metadata
    """
    if st.button("Extract Fields and Metadata", key="extract_fields_btn"):
        try:
            data_mapper.extract_fields()
            st.success("Fields and metadata extracted.")

            # Update session_state
            st.session_state['data_mapper'] = data_mapper

            # Display fields and metadata using Streamlit columns
            st.subheader("Fields and Metadata")
            for source_name, meta in data_mapper.field_metadata.items():
                st.write(f"### Source: {source_name}")
                metadata = meta.get('metadata', {})
                if metadata:
                    # Display fields in columns
                    field_items = list(metadata.items())
                    num_fields = len(field_items)
                    cols_per_row = 3  # Adjust number of columns per row as needed
                    for i in range(0, num_fields, cols_per_row):
                        cols = st.columns(cols_per_row)
                        for idx, (field_name, field_info) in enumerate(field_items[i:i+cols_per_row]):
                            with cols[idx % cols_per_row]:
                                st.markdown(f"**Field:** {field_name}")
                                st.markdown(f"Data Type: {field_info.get('dtype', 'N/A')}")
                                st.markdown(f"Sample Values: {field_info.get('sample_values', [])}")
                else:
                    st.write("No fields found in this source.")

        except Exception as e:
            logger.error(f"Error during field extraction: {str(e)}", exc_info=True)
            st.error("An error occurred while extracting fields. Please check the logs for details.")
            st.exception(e)

@st.fragment
def identify_overlapping_fields_step(data_mapper):
    """
    Step 2: Identify Overlapping Fields
    """
    if st.button("Identify Overlapping Fields", key="identify_overlaps_btn"):
        try:
            overlaps = data_mapper.identify_overlapping_fields()
            st.session_state['data_mapper'] = data_mapper

            if overlaps:
                st.write("### Overlapping Fields Identified:")
                overlapping_field_names = set()
                for overlap in overlaps:
                    overlapping_field_names.add(overlap.get('field_name', 'Unknown'))

                # Display overlaps
                for overlap in overlaps:
                    field_name = overlap.get('field_name', 'Unknown')
                    sources = overlap.get('sources', [])
                    data_types = overlap.get('data_types', {})
                    sample_values = overlap.get('sample_values', {})
                    same_dtype = overlap.get('same_dtype', False)
                    sample_similarity = overlap.get('sample_similarity', {})

                    with st.expander(f"Field: {field_name}"):
                        st.write(f"**Sources:** {', '.join(sources)}")
                        st.write("**Data Types:**")
                        for source_name in sources:
                            st.write(f"- {source_name}: {data_types.get(source_name, 'N/A')}")
                        st.write(f"**Same Data Type:** {'Yes' if same_dtype else 'No'}")
                        st.write("**Sample Values:**")
                        for source_name in sources:
                            st.write(f"- {source_name}: {sample_values.get(source_name, [])}")
                        st.write("**Sample Value Similarity:**")
                        for (source_a, source_b), similarity in sample_similarity.items():
                            st.write(f"- {source_a} vs {source_b}: {similarity:.2f}")

                        # Ask user to confirm
                        confirm_key = f"confirm_{field_name}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = True  # Default to True

                        confirm = st.checkbox(f"Include '{field_name}' in mapping?", value=st.session_state[confirm_key], key=confirm_key)

                # After all checkboxes, reconstruct confirmed_overlaps
                confirmed_overlaps = [overlap for overlap in overlaps if st.session_state.get(f"confirm_{overlap.get('field_name')}", True)]
                st.session_state['confirmed_overlaps'] = confirmed_overlaps
                data_mapper.confirmed_overlaps = confirmed_overlaps
                st.session_state['data_mapper'] = data_mapper
                st.success("Overlapping fields processed.")
                record_action("Identified and confirmed overlapping fields.")
            else:
                st.info("No overlapping fields found.")

        except Exception as e:
            logger.error(f"Error identifying overlapping fields: {str(e)}", exc_info=True)
            st.error("An error occurred while identifying overlapping fields. Please check the logs for details.")
            st.exception(e)

@st.fragment
def establish_hierarchy_step(data_mapper):
    """
    Step 5: Establish Source Hierarchy
    """
    st.subheader("Source Hierarchy")
    source_file_paths = [source['file_path'] for source in data_mapper.data_sources]
    max_levels = len(source_file_paths)

    # Number of hierarchy levels
    num_levels = st.number_input(
        "Specify the number of source hierarchy levels:",
        min_value=1,
        max_value=max_levels,
        value=min(3, max_levels),  # Default to 3 or max_levels
        step=1,
        key="hierarchy_num_levels"
    )

    selected_files = st.session_state.get('selected_files', [])
    source_hierarchy = st.session_state.get('source_hierarchy', selected_files.copy())

    for level in range(1, num_levels + 1):
        remaining_files = [f for f in source_file_paths if f not in selected_files]
        if not remaining_files and level > len(selected_files):
            st.warning("No more files available to select for hierarchy.")
            break

        selectbox_key = f"hierarchy_level_{level}"

        # Initialize selected file from session_state if available
        if selectbox_key not in st.session_state:
            if level <= len(selected_files):
                st.session_state[selectbox_key] = selected_files[level-1]
            else:
                st.session_state[selectbox_key] = remaining_files[0] if remaining_files else ''

        selected_file = st.selectbox(
            f"Select source file for level {level} (1 is highest priority):",
            options=remaining_files if level > len(selected_files) else [st.session_state[selectbox_key]] + remaining_files,
            key=selectbox_key
        )

        if selected_file:
            if level <= len(selected_files):
                selected_files[level-1] = selected_file
            else:
                selected_files.append(selected_file)
            source_hierarchy = selected_files.copy()
            st.session_state['selected_files'] = selected_files
            st.session_state['source_hierarchy'] = source_hierarchy

    if st.button("Set Source Hierarchy", key="set_hierarchy_btn"):
        if not source_hierarchy:
            st.error("Please select at least one source file for hierarchy.")
            return
        data_mapper.source_hierarchy = source_hierarchy
        st.session_state['data_mapper'] = data_mapper
        st.success("Source hierarchy established.")
        record_action("User established source hierarchy and weights.")

@st.fragment
def create_mapping_dictionary_step(data_mapper):
    """
    Step 3: Create Mapping Dictionary
    """
    st.subheader("Field Mapping")
    if st.button("Create Mapping Dictionary", key="create_mapping_btn"):
        try:
            if not data_mapper.source_hierarchy:
                st.error("Source hierarchy is not established. Please establish source hierarchy first.")
                return

            # Initialize mapping dictionary
            data_mapper.mapping_dictionary = {}
            st.session_state['data_mapper'] = data_mapper
            st.session_state['anchor_fields'] = []

            anchor_fields = []

            # Collect overlapping field names
            overlapping_field_names = set()
            for overlap in data_mapper.confirmed_overlaps:
                overlapping_field_names.add(overlap.get('field_name', ''))

            # Start mapping from the highest priority source
            for idx, source in enumerate(data_mapper.source_hierarchy):
                data_mapper = mapping_fields_for_source(data_mapper, source, idx, overlapping_field_names)

            st.session_state['data_mapper'] = data_mapper
            st.success("Mapping dictionary created.")
            record_action("User created mapping dictionary.")

        except Exception as e:
            logger.error(f"Error creating mapping dictionary: {str(e)}", exc_info=True)
            st.error("An error occurred while creating the mapping dictionary. Please check the logs for details.")
            st.exception(e)

@st.fragment
def mapping_fields_for_source(data_mapper, source, idx, overlapping_field_names):
    """
    Map fields for a given source based on hierarchy level.
    """
    st.write(f"### Mapping fields for source '{source}' (Level {idx+1})")
    # Find the file name from file_path
    source_file = next((s['file'] for s in data_mapper.data_sources if s['file_path'] == source), None)
    if not source_file:
        st.error(f"Source file '{source}' not found in data sources.")
        return data_mapper  # Exit the function

    source_fields = list(data_mapper.field_metadata.get(source_file, {}).get('metadata', {}).keys())
    st.write(f"Fields from '{source_file}': {source_fields}")

    if idx == 0:
        # Highest priority source: use its fields as anchor fields
        for field in source_fields:
            data_mapper.mapping_dictionary[field] = [(source_file, field)]
        anchor_fields = list(data_mapper.mapping_dictionary.keys())
        st.write(f"Anchor fields from '{source_file}': {anchor_fields}")
        # Save anchor_fields to session_state
        st.session_state['anchor_fields'] = anchor_fields
    else:
        # For lower priority sources, map their fields
        for field in source_fields:
            st.write(f"#### Field '{field}' from source '{source_file}'")
            # Determine if the field is overlapping
            is_overlapping = field in overlapping_field_names

            # Define mapping options based on overlap
            if is_overlapping:
                mapping_options = ['Map to anchor field', 'Map to new field', 'Leave as is']
                default_option = 'Map to anchor field'
            else:
                mapping_options = ['Map to new field', 'Leave as is']
                default_option = 'Leave as is'

            mapping_option_key = f"mapping_option_{source_file}_{field}"
            
            if mapping_option_key not in st.session_state:
                st.session_state[mapping_option_key] = default_option  # Set default based on overlap

            selected_option = st.selectbox(
                f"Select mapping option for field '{field}' from '{source_file}'",
                mapping_options,
                key=mapping_option_key
            )

            if selected_option == 'Map to anchor field':
                # User selects which anchor field to map to
                anchor_field_key = f"anchor_field_{source_file}_{field}"
                if anchor_field_key not in st.session_state:
                    st.session_state[anchor_field_key] = st.session_state['anchor_fields'][0] if st.session_state['anchor_fields'] else ''

                selected_anchor_field = st.selectbox(
                    f"Select anchor field to map '{field}' to",
                    options=st.session_state['anchor_fields'],
                    key=anchor_field_key
                )

                if selected_anchor_field:
                    data_mapper.mapping_dictionary[selected_anchor_field].append((source_file, field))
            elif selected_option == 'Map to new field':
                new_field_key = f"new_field_{source_file}_{field}"
                if new_field_key not in st.session_state:
                    st.session_state[new_field_key] = ''

                new_field_name = st.text_input(
                    f"Specify new field name for '{field}'",
                    key=new_field_key
                )

                if new_field_name:
                    if new_field_name not in data_mapper.mapping_dictionary:
                        data_mapper.mapping_dictionary[new_field_name] = []
                        if new_field_name not in st.session_state['anchor_fields']:
                            st.session_state['anchor_fields'].append(new_field_name)  # Avoid duplicates
                    data_mapper.mapping_dictionary[new_field_name].append((source_file, field))
            else:
                # Leave as is
                if field not in data_mapper.mapping_dictionary:
                    data_mapper.mapping_dictionary[field] = []
                    if field not in st.session_state['anchor_fields']:
                        st.session_state['anchor_fields'].append(field)  # Avoid duplicates
                data_mapper.mapping_dictionary[field].append((source_file, field))

    return data_mapper

@st.fragment
def save_mapping_dictionary_step(data_mapper):
    """
    Step 4: Save Mapping Dictionary
    """
    if st.button("Save Mapping Dictionary", key="save_mapping_btn"):
        try:
            data_mapper.save_mapping()
            st.success("Mapping dictionary saved.")
            record_action("User saved mapping dictionary.")
        except Exception as e:
            logger.error(f"Error saving mapping dictionary: {str(e)}", exc_info=True)
            st.error("An error occurred while saving the mapping dictionary. Please check the logs for details.")
            st.exception(e)

@st.fragment
def align_data_structures_step(data_mapper):
    """
    Step 6: Align Data Structures
    """
    if st.button("Align Data Structures", key="align_structures_btn"):
        try:
            if not data_mapper.mapping_dictionary:
                st.error("Mapping dictionary is empty. Please create the mapping dictionary before aligning structures.")
                return
            data_mapper.align_structures()
            st.session_state['data_mapper'] = data_mapper
            st.success("Data structures aligned.")
            record_action("User aligned data structures.")
        except Exception as e:
            logger.error(f"Error aligning data structures: {str(e)}", exc_info=True)
            st.error("An error occurred while aligning data structures. Please check the logs for details.")
            st.exception(e)

@st.fragment
def save_temporary_merged_file_step(data_mapper):
    """
    Step 7: Save Temporary Merged File
    """
    st.subheader("Save Temporary Merged File")
    temp_file_name_key = "temp_file_name_input"
    if temp_file_name_key not in st.session_state:
        st.session_state[temp_file_name_key] = ""

    temp_file_name = st.text_input("Specify a file name for the temporary merged file:", key=temp_file_name_key)

    if st.button("Merge and Save Temporary File", key="merge_save_temp_btn"):
        try:
            if not data_mapper.mapping_dictionary:
                st.error("Mapping dictionary is empty. Please create the mapping dictionary before merging.")
                return
            if not temp_file_name.strip():
                st.error("Please specify a valid file name.")
                return

            # Determine the temp folder path based on the first data source's directory
            if data_mapper.data_sources:
                first_source_path = data_mapper.data_sources[0]['file_path']
                source_dir = os.path.dirname(first_source_path)
                temp_dir = os.path.join(source_dir, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                temp_file_path = os.path.join(temp_dir, temp_file_name)
            else:
                st.error("No data sources available to determine the temp directory.")
                return

            data_mapper.merge_data_sources()
            data_mapper.save_temporary_merged_file(temp_file_path)
            st.success(f"Temporary merged file saved as '{temp_file_path}'.")
            st.session_state['temp_merged_file'] = temp_file_path

            # Load the temp merged file
            data_mapper.load_temporary_merged_file(temp_file_path)
            st.session_state['data_mapper'] = data_mapper

            # **Set resolved_data in session_state**
            if hasattr(data_mapper, 'resolved_data') and data_mapper.resolved_data is not None:
                st.session_state['resolved_data'] = data_mapper.resolved_data

            # Automatically run conflict detection and data type verification
            detect_and_resolve_conflicts_step(data_mapper)
            verify_and_convert_data_types_step(data_mapper)

            record_action(f"User saved temporary merged file '{temp_file_path}'.")

        except Exception as e:
            logger.error(f"Error during merging and saving temporary file: {str(e)}", exc_info=True)
            st.error(f"An error occurred during merging: {str(e)}")
            st.exception(e)

@st.fragment
def detect_and_resolve_conflicts_step(data_mapper):
    """
    Step 8: Detect and Resolve Conflicts
    """
    if 'temp_merged_file' not in st.session_state:
        st.info("Please save a temporary merged file before detecting conflicts.")
        return

    st.subheader("Conflict Detection and Resolution")

    conflict_strategies = ["Manual", "Time-based", "Hierarchy-based", "Weight-based"]
    conflict_strategy_key = "conflict_strategy_select"
    if conflict_strategy_key not in st.session_state:
        st.session_state[conflict_strategy_key] = "Manual"

    selected_strategy = st.selectbox(
        "Select Conflict Resolution Strategy",
        conflict_strategies,
        key=conflict_strategy_key
    )
    st.session_state['conflict_strategy'] = selected_strategy

    if st.button("Detect Conflicts", key="detect_conflicts_btn"):
        try:
            temp_file_path = st.session_state['temp_merged_file']
            data_mapper.load_temporary_merged_file(temp_file_path)
            data_mapper.detect_conflicts(report_row_numbers=True)
            st.session_state['data_mapper'] = data_mapper

            if data_mapper.conflicts:
                st.write("### Conflicts Detected:")
                for keys, conflict in data_mapper.conflicts.items():
                    st.write(f"**Conflict at keys:** {keys}")
                    for field, details in conflict.items():
                        st.write(f"- **Field:** {field}")
                        for source, info in details.items():
                            st.write(f"  - **Source:** {source}")
                            st.write(f"    - **Values:** {info.get('values', [])}")
                            st.write(f"    - **Rows:** {info.get('rows', [])}")

                if selected_strategy == "Manual":
                    st.write("### Manual Conflict Resolution:")
                    for conflict_key, conflict_fields in data_mapper.conflicts.items():
                        st.write(f"**Conflict at keys:** {conflict_key}")
                        for field, field_conflict in conflict_fields.items():
                            st.write(f"**Field:** {field}")
                            # Display conflicting rows
                            conflicting_rows = data_mapper.get_conflicting_rows(conflict_key, field)
                            st.write(conflicting_rows)
    
                            # Allow user to choose action
                            action_key = f"conflict_action_{conflict_key}_{field}"
                            if action_key not in st.session_state:
                                st.session_state[action_key] = 'Keep First'  # Default action
    
                            action = st.selectbox(
                                f"Action for conflict at {conflict_key} in field '{field}'",
                                options=['Keep First', 'Delete Rows', 'Edit Values'],
                                key=action_key
                            )
                            # No assignment to st.session_state[action_key]
    
                            if action == 'Delete Rows':
                                data_mapper.mark_rows_for_deletion(conflict_key, field)
                                st.write(f"Rows marked for deletion for field '{field}' at keys {conflict_key}.")
                            elif action == 'Edit Values':
                                edit_value_key = f"edit_value_{conflict_key}_{field}"
                                if edit_value_key not in st.session_state:
                                    st.session_state[edit_value_key] = ""
    
                                new_value = st.text_input(
                                    f"New value for field '{field}' at {conflict_key}",
                                    key=edit_value_key
                                )
                                # No assignment to st.session_state[edit_value_key]
    
                                if new_value:
                                    data_mapper.update_conflict_value(conflict_key, field, new_value)
                                    st.write(f"Value updated for field '{field}' at keys {conflict_key}.")
                    st.session_state['data_mapper'] = data_mapper
                    st.success("Manual conflict resolution actions applied.")
                    record_action("User performed manual conflict resolution.")
                else:
                    st.write(f"Conflicts will be resolved using the '{selected_strategy}' strategy.")
                    st.session_state['conflict_strategy'] = selected_strategy
                    st.session_state['conflicts_detected'] = True
            else:
                st.success("No conflicts detected.")
                # **Set resolved_data in session_state**
                data_mapper.resolved_data = data_mapper.merged_data
                st.session_state['data_mapper'] = data_mapper
                st.session_state['resolved_data'] = data_mapper.resolved_data
                st.session_state['conflicts_detected'] = False
                verify_and_convert_data_types_step(data_mapper) 

        except Exception as e:
            logger.error(f"Error during conflict detection: {str(e)}", exc_info=True)
            st.error(f"An error occurred during conflict detection: {str(e)}")
            st.exception(e)

    if st.session_state.get('conflicts_detected', False):
        if st.button("Resolve Conflicts", key="resolve_conflicts_btn"):
            try:
                temp_file_path = st.session_state['temp_merged_file']
                output_file_name = f"fixed_conflicts_{os.path.basename(temp_file_path)}"
                output_file_path = os.path.join(os.path.dirname(temp_file_path), output_file_name)
                selected_strategy = st.session_state.get('conflict_strategy', "Manual")
                data_mapper.resolve_conflicts(selected_strategy)
                data_mapper.save_resolved_data(output_file_path)
                st.success(f"Conflicts resolved and data saved to '{output_file_path}'.")
                # **Set resolved_data in session_state**
                data_mapper.resolved_data = data_mapper.resolved_data  # Assuming resolve_conflicts updates resolved_data
                st.session_state['resolved_data'] = data_mapper.resolved_data
                record_action(f"User resolved conflicts and saved data to '{output_file_path}'.")
            except Exception as e:
                logger.error(f"Error during conflict resolution: {str(e)}", exc_info=True)
                st.error(f"An error occurred during conflict resolution: {str(e)}")
                st.exception(e)

@st.fragment
def verify_and_convert_data_types_step(data_mapper):
    """
    Step 9: Verify and Convert Data Types
    """
    st.subheader("Data Type Verification and Conversion")
    if hasattr(data_mapper, 'resolved_data'):
        incompatibilities = verify_data_types([{'data': data_mapper.resolved_data}])
        if incompatibilities:
            st.warning("Data type incompatibilities found:")
            st.write(incompatibilities)
            # Allow user to select conversions
            user_conversions = st.session_state.get('user_conversions', {})
            for field, types in incompatibilities.items():
                st.write(f"**Field '{field}'** has incompatible types: {types}")
                conversion_key = f"convert_{field}"
                if conversion_key not in st.session_state:
                    st.session_state[conversion_key] = 'int'  # Default conversion type

                selected_type = st.selectbox(
                    f"Convert '{field}' to type:",
                    options=['int', 'float', 'str', 'datetime'],
                    key=conversion_key
                )

                # No need to assign st.session_state[conversion_key] = selected_type
                user_conversions[field] = selected_type

            st.session_state['user_conversions'] = user_conversions

            if st.button("Convert Data Types", key="convert_data_types_btn"):
                try:
                    conversions = st.session_state.get('user_conversions', {})
                    data_mapper.verify_and_convert_data_types(conversions)
                    st.session_state['data_mapper'] = data_mapper
                    # **Set resolved_data in session_state**
                    st.session_state['resolved_data'] = data_mapper.resolved_data
                    st.success("Data types converted.")
                    record_action("User converted data types.")
                except Exception as e:
                    logger.error(f"Error during data type conversion: {str(e)}", exc_info=True)
                    st.error("An error occurred while converting data types. Please check the logs for details.")
                    st.exception(e)
        else:
            st.info("No data type incompatibilities found.")
    else:
        st.info("Please resolve conflicts before verifying data types.")
