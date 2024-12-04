# Entity_Bridge.py

app_version = "0.1"
app_title = "OllaLab - Entity Bridge"
app_description = "Seamlessly merge multiple datasets based on entity names"
app_icon = ":link:"

import streamlit as st
from entity_bridge import data_loader
from entity_bridge import data_normalizer
from entity_bridge import duplicate_remover
from entity_bridge import entity_matcher
from entity_bridge import ui_helper

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
else:
    st.warning("Please upload at least two files to proceed.")

if data_frames:
    st.header("Normalizing Data and Checking for Similar Names")
    # Step 3: Normalize IDs and Names, check and merge similar names within data frames
    normalized_data_frames = data_normalizer.normalize_data_frames(data_frames)

    st.header("Removing Duplicates from Data Frames")
    # Step 4: Remove Duplicates (now includes displaying duplicates and removed rows)
    deduplicated_data_frames = duplicate_remover.remove_duplicates_from_data_frames(normalized_data_frames)

    st.header("Matching Entities Across Data Frames and Assigning Unique Identifiers")
    # Step 5: Construct Unique Parent List
    unique_parents_df = entity_matcher.construct_unique_parent_list(deduplicated_data_frames)

    # Step 6: Construct Unique Child List
    unique_children_df = entity_matcher.construct_unique_child_list(deduplicated_data_frames)

    # Step 7: Enrich DataFrames with Unique IDs
    enriched_data_frames = entity_matcher.enrich_data_frames_with_unique_ids(
        deduplicated_data_frames, unique_parents_df, unique_children_df
    )

    # Step 8: Display Enriched DataFrames
    ui_helper.display_enriched_data(enriched_data_frames)

    # Step 9: Download Enriched DataFrames
    ui_helper.download_enriched_data(enriched_data_frames)
else:
    st.warning("Please upload at least two files to proceed.")