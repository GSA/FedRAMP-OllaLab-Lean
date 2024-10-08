# components/import_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_import import import_files_parallel, apply_data_fixes
from data_unificator.utils.file_utils import get_supported_files, save_file
from data_unificator.audits.audit_trail import record_action
import os
import pandas as pd

logger = get_logger(__name__)

@st.fragment
def handle_manual_hierarchy(df, file_path):
    file_name = os.path.basename(file_path)
    st.subheader(f"Specify Data Hierarchy for '{file_name}'")
    # Initialize hierarchy data structures
    if 'manual_hierarchy' not in st.session_state:
        st.session_state['manual_hierarchy'] = {}
    if 'assigned_nodes' not in st.session_state:
        st.session_state['assigned_nodes'] = {}
    if file_name not in st.session_state['manual_hierarchy']:
        st.session_state['manual_hierarchy'][file_name] = {}
    if file_name not in st.session_state['assigned_nodes']:
        st.session_state['assigned_nodes'][file_name] = set()  

    columns = df.columns.tolist()
    assigned_nodes = st.session_state['assigned_nodes'][file_name]
    available_columns = [col for col in columns if col not in assigned_nodes]

    # Select top level nodes
    level_1_nodes = st.multiselect(
        f"Select Top-level Nodes",
        options=available_columns,
        key=f"top_level_nodes_{file_name}"
    )
    # Update assigned nodes
    assigned_nodes.update(level_1_nodes)

    # Function to recursively get children of a top-levle node
    def recursive_hierarchy (node):
        available_columns = [col for col in columns if col not in assigned_nodes]
        if not available_columns:
            return
        children = st.multiselect(
            f"Select children of '{node}'",
            options=available_columns,
            key=f"children_{file_name}_{node}"
        )
        st.session_state['manual_hierarchy'][file_name][node] = children
        # update assigned nodes
        assigned_nodes.update(children)
        # specify a child's children
        for child in children:
            recursive_hierarchy(child)
    for node in level_1_nodes:
        recursive_hierarchy(node)

    # Check for consistency
    if st.button(f"Validate Hierarchy"):
        hierarchy = st.session_state['manual_hierarchy'][file_name]
        if check_hierarchy_consistency(hierarchy):
            st.success(f"Hierarchy for '{file_name}' is consistent.")
            # store hierarchy data
            st.session_state['hierarchy_data'][file_name] = hierarchy
            # visualize hierarchy
            hierarchy_graph = extract_hierarchy(manual_hierarchy=hierarchy)
            hierarchy_image_path = os.path.join(
                os.path.dirname(file_path),
                f"{file_name.replace('.','_')}_hierarchy.png"
            )
            visualize_hierarchy(hierarchy_graph, save_path=hierarchy_image_path)
            if os.path.exists(hierarchy_image_path):
                st.image(hierarchy_image_path, caption=f"{file_name} Data Hierarchy")
    else:
        st.error(f"Hierarchy for '{file_name}' is inconsistent. Please revise.")

def check_hierarchy_consistency(hierarchy):
    # flatten hierarchy to parent-child pairs
    parent_child_pairs = []
    for parent, children in hierarchy.items():
        for child in children:
            parent_child_pairs.apptend((parent,child))
    
    # Reconstruct the hierarchy graph and compare for inconsistencies
    G = nx.DiGraph()
    G.add_edges_from(parent_child_pairs)
    try:
        cycles = list(nx.find_cycle(G, orientation='original'))
        if cycles:
            return False
    except nx.exception.NetworkXNoCycle:
        pass

    # check for multiple parents
    node_parents = {}
    for parent, child in parent_child_pairs:
        if child in node_parents and node_parents[child] != parent:
            return False # child has multiple parents
        node_parents[child] = parents

    return True

@st.fragment
def handle_missing_data(df,missing_data_info,file_name):
    st.subheader(f"Missing Data in '{file_name}'")
    for field, count in missing_data_info.items():
        col1, col2 = st.columns(2)
        exist_count = df[field].count()
        field_type = df[field].dtype

        if pd.api.types.is_numeric_dtype(df[field]):
            available_strategies = [
                "Statistical Imputation", "Predictive Model",
                "Deletion", "Manual Input"
            ]
        else:
            available_strategies = ["Manual Input", "Deletion"]

        # Display the data
        with col1:
            st.write(f"**Field: {field}**")
            st.write(f"Type: {field_type}")
            st.write(f"Missing values: {count}/{count + exist_count}")
        with col2:
            selected_strategy = st.selectbox(
                label=f"Strategy: ",
                options=available_strategies,
                key=f"strategy_{file_name}_{field}"
            )

            # Store strategy for the field
            st.session_state['missing_data_strategies'][f"{file_name}_{field}"] = selected_strategy

            # Allow manual input if selected
            if selected_strategy == "Manual Input":
                manual_value = st.text_input(
                    label=f"Input value: ",
                    value="some_value",
                    key=f"manual_input_{file_name}_{field}"
                )
                st.session_state['manual_inputs'][f"{file_name}_{field}"] = manual_value

@st.fragment
def handle_pii(pii_fields,file_name):
    st.subheader(f"PII Data in '{file_name}'")
    st.write(f"PII Fields: {pii_fields}")
    for pii_field in pii_fields:
        action = st.selectbox(
            label=f"Action for PII field '{pii_field}' in '{file_name}'",
            options=["Remove Field", "Anonymize Field"],
            key=f"pii_action_{file_name}_{pii_field}"
        )
        st.session_state['pii_actions'][f"{file_name}_{pii_field}"] = action

def render_import(num_workers):
    st.header("Data Import")
    st.write("Please select the folder containing your data files.")

    # Initialize session state variables with appropriate default values
    session_state_defaults = {
        'results': [],                      # List to store results
        'missing_data_strategies': {},      # Dictionary for missing data strategies
        'data_imported': False,             # Boolean flag
        'manual_inputs': {},                # Dictionary for manual inputs
        'pii_actions': {},                  # Dictionary for PII actions
        'results_to_fix': [],               # List to store results needing fixes
        'hierarchy_data': {}                # Dictionary for hierarchy data
    }

    for var, default_value in session_state_defaults.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

    folder = st.text_input("Folder Path", "app_data/data_unificator")
    start_import = st.button("Start Import")

    if start_import or st.session_state['data_imported']:
        if not os.path.isdir(folder):
            st.error("Invalid folder path. Please enter a valid directory.")
            return

        # Get list of supported files, excluding backup folder
        file_paths = get_supported_files(folder, exclude_backup=True)
        if not file_paths:
            st.warning("No supported data files found in the selected folder.")
            return

        st.write(f"Found {len(file_paths)} files to import.")

        # Record action
        if not st.session_state['data_imported']:
            record_action(f"Data Import - {len(file_paths)} files from '{folder}'")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                results = []
                for i, result in enumerate(import_files_parallel(file_paths, num_workers)):
                    progress = (i + 1) / len(file_paths)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {i + 1} of {len(file_paths)}")

                    results.append(result)

                st.session_state['results'] = results
                st.session_state['data_imported'] = True

            except Exception as e:
                logger.error(f"Data Import - {str(e)}", exc_info=True)
                st.error("An error occurred during import. Please check the logs for details.")
                st.exception(e)
                st.stop()
            finally:
                progress_bar.empty()
                status_text.empty()
        else:
            results = st.session_state['results']

        all_files_handled = True

        for result in results:
            file_name = result['file']
            st.write(f"Skipped Entries: {result.get('skipped_entries', 0)} for '{file_name}'")
            original_file_path =  result.get('file_path')
            if result['status'] == 'issues_found':
                st.warning(f"Issues found in '{file_name}'")
                df = result['data']
                st.session_state['results_to_fix'].append(result)

                # Handle missing data
                missing_data_info = result.get('missing_data_info')
                if missing_data_info is not None and not missing_data_info.empty:
                    handle_missing_data(df,missing_data_info,file_name)

                # Handle PII fields
                if result.get('pii_fields'):
                    handle_pii(result.get('pii_fields'),file_name)

                # Handle discrepancies
                discrepancies = result.get('discrepancies')
                if discrepancies:
                    st.subheader(f"Discrepancies in '{file_name}'")
                    for discrepancy in discrepancies:
                        st.write(f"- {discrepancy}")

            elif result['status'] == 'success':
                st.success(f"Successfully imported '{file_name}'")
                df = result['data']
                # Save the modified DataFrame back to a CSV file
                csv_path = save_file(df, original_file_path)
                # Display EDA report
                with st.expander(f"EDA Report for '{os.path.basename(file_name)}'"):
                    if result.get('eda_report'):
                        st.components.v1.html(result['eda_report'], height=600, scrolling=True)
                    else:
                        st.write("No EDA report available.")
                # Store hierarchy data for next phase
                st.session_state['hierarchy_data'][file_name] = result.get('hierarchy_data')
                # Display data hierarchy visualization
                hierarchy_image_path = os.path.join(
                    os.path.dirname(file_paths[0]),
                    f"{file_name.replace('.', '_')}_hierarchy.png"
                )
                if os.path.exists(hierarchy_image_path):
                    st.image(hierarchy_image_path, caption=f"{file_name} Data Hierarchy")
                else:
                    st.write("Data hierarchy visualization not available.")
            elif result['status'] == 'error':
                st.error(f"Error importing '{file_name}': {result['error']}")

        # Check if there are any issues to fix
        has_issues_to_fix = len(st.session_state['results_to_fix']) > 0

        if has_issues_to_fix:
            if st.button("Fix Data Issues"):
                for result in st.session_state['results_to_fix']:
                    file_name = result['file']
                    original_file_path = [
                        fp for fp in file_paths if os.path.basename(fp) == file_name
                    ][0]

                    # Prepare the strategies and actions
                    missing_data_strategies = {
                        k.split('_', 1)[1]: v
                        for k, v in st.session_state['missing_data_strategies'].items()
                        if k.startswith(f"{file_name}_")
                    }
                    manual_inputs = {
                        k.split('_', 1)[1]: v
                        for k, v in st.session_state['manual_inputs'].items()
                        if k.startswith(f"{file_name}_")
                    }
                    pii_actions = {
                        k.split('_', 1)[1]: v
                        for k, v in st.session_state['pii_actions'].items()
                        if k.startswith(f"{file_name}_")
                    }
                    discrepancies = result.get('discrepancies')

                    # Apply fixes
                    success, hierarchy = apply_data_fixes(
                        original_file_path,
                        missing_data_strategies=missing_data_strategies,
                        manual_inputs=manual_inputs,
                        pii_actions=pii_actions,
                        discrepancies=discrepancies
                    )
                    if success:
                        st.success(f"Fixed data issues in '{file_name}'")
                        record_action(f"Applied data fixes to '{file_name}'")
                        # Update hierarchy data
                        st.session_state['hierarchy_data'][file_name] = hierarchy
                    else:
                        st.error(f"Failed to fix data issues in '{file_name}'")

                # Reset data import state to allow re-import
                st.session_state['data_imported'] = False

                if st.button("Re-import Data"):
                    # Clear session state variables related to data import
                    for var in ['results', 'missing_data_strategies', 'manual_inputs',
                                'pii_actions', 'results_to_fix']:
                        st.session_state[var] = {} if 'dict' in var or 'results' in var else False
                    # Re-run the data import process
                    render_import(num_workers)
