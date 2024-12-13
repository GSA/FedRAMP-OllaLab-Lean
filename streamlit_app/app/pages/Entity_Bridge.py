# Entity_Bridge.py

app_version = "0.1"
app_title = "OllaLab - Entity Bridge"
app_description = "Seamlessly merge multiple datasets based on entity names"
app_icon = ":link:"

import os
import streamlit as st
from entity_bridge import data_loader
from entity_bridge import data_normalizer
from entity_bridge import duplicate_remover
from entity_bridge import entity_matcher
from entity_bridge import ui_helper
from entity_bridge import llm_integration
from entity_bridge import utils

if 'proceed1' not in st.session_state:
    st.session_state['proceed1'] = False
if 'proceed2' not in st.session_state:
    st.session_state['proceed2'] = False

def process_file(file, idx):
    """
    Process a single uploaded file, including loading, handling missing data,
    field selection, and initial data preparation.

    Args:
        file (UploadedFile): The file uploaded by the user.
        idx (int): Index of the file in the list of uploaded files.

    Returns:
        tuple: A tuple (DataFrame, selected_fields), where DataFrame is the
        processed DataFrame, and selected_fields is a dictionary of selected fields.

    Side Effects:
        Displays messages and widgets in the Streamlit UI.
    """
    st.header(f"Processing file: {file.name}")

    try:
        # Load the data
        df = data_loader.load_data(file)
        st.success(f"Successfully loaded {file.name}")

        # Display the first few rows of the data
        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Handle missing data
        strategy, default_value, missing_threshold = ui_helper.display_missing_data_options(idx, file.name)

        if strategy == 'remove':
            df = data_loader.handle_missing_data(df, 'remove')
        elif strategy == 'fill':
            df = data_loader.handle_missing_data(df, 'fill', default_value=default_value)
        elif strategy == 'skip':
            df = data_loader.handle_missing_data(df, 'skip', missing_threshold=missing_threshold)
        else:
            st.error("Invalid strategy selected for handling missing data.")
            return None, None

        # Field selection
        selected_fields = ui_helper.display_field_selection(df, file.name, idx)

        #if not selected_fields.get('parent_name'):
            #st.error("Parent Name Field is mandatory. Cannot proceed without it.")
            #return None, None

        # Ensure required columns are in the DataFrame
        required_columns = [field for field in selected_fields.values() if field]
        df_selected = df[required_columns].copy()

        st.success(f"File {file.name} processed successfully.")
        return df_selected, selected_fields

    except Exception as e:
        st.error(f"An error occurred while processing {file.name}: {e}")
        return None, None

st.title("Entity Bridge")
st.write("Merge multiple datasets containing entity information with overlapping entities.")

# Step 1: File Upload
uploaded_files = ui_helper.display_file_upload()

data_frames = []

if uploaded_files and len(uploaded_files) >= 2:
    # Step 2: Load and preprocess the data files
    for idx, file in enumerate(uploaded_files):
        df_selected, selected_fields = process_file(file, idx)
        if df_selected is not None and selected_fields:
            data_frames.append((df_selected, selected_fields))
        else:
            st.error(f"Failed to process file {file.name}.")

if data_frames:
    st.session_state['proceed1']=True

if st.button("Reset",key="reset1"):
    st.session_state['proceed1']=False
    st.session_state['proceed2']=False

if st.session_state['proceed1']:
    st.header("Normalizing Data and Checking for Similar Names")

    # Get custom stopwords from the user
    parent_custom_stopwords, child_custom_stopwords = ui_helper.get_custom_stopwords()

    # Step 3: Normalize IDs and Names, check and merge similar names within data frames
    normalized_data_frames = data_normalizer.normalize_data_frames(
        data_frames,
        parent_custom_stopwords=parent_custom_stopwords,
        child_custom_stopwords=child_custom_stopwords
        )

    if st.button("Proceed with later steps"):
        st.session_state['proceed2'] = True
    if st.button("Reset",key="reset2"):
        st.session_state['proceed1']=False
        st.session_state['proceed2']=False

    if st.session_state['proceed2']:
        st.header("Removing Duplicates from Data Frames")
        # Step 4: Remove Duplicates (now includes displaying duplicates and removed rows)
        deduplicated_data_frames = duplicate_remover.remove_duplicates_from_data_frames(normalized_data_frames)

        st.header("Matching Entities Across Data Frames and Assigning Unique Identifiers")
        # Step 5: Construct Unique Parent List
        unique_parents_df = entity_matcher.construct_unique_parent_list(deduplicated_data_frames)
        
        # After constructing unique_parents_df
        use_llm = st.radio("Do you want to leverage LLM for further identifying unique parents?", ["Yes", "No"], key="use_llm")

        if use_llm == 'Yes':

            st.write ("Please first refer to the left sidebar to configure the LLM endpoint.")
            
            parent_entity_type = st.text_input("Please input the type of the parent entity (e.g., 'parent company')", key="parent_entity_type")

            parent_names_list = unique_parents_df['ParentName'].tolist()

            # Display LLM configuration in the sidebar
            with st.sidebar:
                llm_settings = ui_helper.display_llm_configuration()

            if st.button("Continue", key="llm_continue"):

                # Construct the prompt
                parent_names_str = ', '.join(parent_names_list)
                prompt = f"""Given the following list of entities: [{parent_names_str}],
        Based on your knowledge of real-world relationships, determine if it is plausible to group some of these entities that share a common parent entity of type "{parent_entity_type}".
        For each identified group, identify the name of the potential parent entity that could encompass all of the group's members.
        Respond only with valid JSON. Do not write an introduction or summary.
        The JSON format should be:
        {{
        "groups": [
            {{
            "parent": "Name of the group parent entity",
            "members": ["Member entity name 1", "Member entity name 2", ...]
            }},
            ...
        ]
        }}
        """

                # Set up LLM client
                try:
                    client = llm_integration.setup_llm_client(
                        provider=llm_settings['provider'],
                        **llm_settings['credentials']
                    )
                except Exception as e:
                    st.error(f"Error setting up LLM client: {e}")
                    st.stop()

                # Generate entity mappings
                try:
                    entity_mappings = llm_integration.generate_entity_mappings_with_llm(
                        prompt=prompt,
                        client=client,
                        provider=llm_settings['provider'],
                        model_name=llm_settings['model_name']
                    )
                except Exception as e:
                    st.error(f"Error generating entity mappings with LLM: {e}")
                    st.stop()

                # Process the result
                # Ensure entity_mappings is a dict with 'groups'
                if 'groups' not in entity_mappings:
                    st.error("LLM response does not contain 'groups'.")
                    st.stop()

                # Remove group members not in parent_names_list
                valid_groups = []
                for group in entity_mappings.get('groups', []):
                    group_members = group.get('members', [])
                    group_members = [name for name in group_members if name in parent_names_list]
                    if group.get('parent') and len(group_members) >= 2:
                        group['members'] = group_members
                        valid_groups.append(group)

                # Ask users to confirm the groups
                st.subheader("Please confirm the following groups identified by the LLM:")
                confirmed_groups = []
                for idx, group in enumerate(valid_groups):
                    st.write(f"**Group {idx+1}:**")
                    st.write(f"**Group Parent:** {group['parent']}")
                    st.write(f"**Group Members:** {', '.join(group['members'])}")
                    confirm = st.checkbox(f"Confirm this group", key=f"group_confirm_{idx}")
                    if confirm:
                        confirmed_groups.append(group)

                if st.button("Apply Confirmed Groups", key="llm_groups_continue"):

                    # For each confirmed group, generate a unique ID for the group's parent, map group member IDs
                    for group in confirmed_groups:
                        group_parent_id = utils.generate_unique_identifier()
                        group_members = group['members']
                        group_parent_name = group['parent']

                        # Update unique_parents_df
                        for member_name in group_members:
                            unique_parents_df.loc[unique_parents_df['ParentName'] == member_name, 'UniqueParentID'] = group_parent_id
                        # Optionally, you may want to add a new row for the group parent
                        #unique_parents_df = unique_parents_df.append({
                            #'ParentName': group_parent_name,
                            #'UniqueParentID': group_parent_id
                        #}, ignore_index=True)

                        st.write(f"**Group Parent ID:** {group_parent_id}")
                        st.write(f"**Group Parent Name:** {group_parent_name}")
                        st.write(f"**Group Members:** {', '.join(group_members)}")

                else:
                    st.stop()  # Wait until user applies the groups

        # Proceed to Enrich DataFrames with Unique IDs using the updated unique_parents_df
        enriched_data_frames = entity_matcher.enrich_data_frames_with_unique_ids(
            deduplicated_data_frames, unique_parents_df, entity_type='parent'
        )

        # Step 6: Construct Unique Child List
        unique_children_df = entity_matcher.construct_unique_child_list(deduplicated_data_frames)

        # Step 7: Enrich DataFrames with Unique IDs
        # Need rework: might work best if enrich with parent id only.
        enriched_data_frames = entity_matcher.enrich_data_frames_with_unique_ids(
            deduplicated_data_frames, unique_children_df,entity_type='child'
        )

        # Step 8: Display Enriched DataFrames
        ui_helper.display_enriched_data(enriched_data_frames)

        # Step 9: Download Enriched DataFrames
        ui_helper.download_enriched_data(enriched_data_frames)