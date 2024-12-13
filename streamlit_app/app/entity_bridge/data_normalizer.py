# streamlit_app/app/entity_bridge/data_normalizer.py

"""
Data Normalizer Module

This module includes functions to normalize IDs and entity names to ensure consistency.
"""

import pandas as pd
import streamlit as st
from entity_bridge.utils import (
    generate_unique_identifier,
    normalize_text,
    log_normalization_actions,
    calculate_similarity
)

def check_and_merge_similar_names(df, selected_fields, entity_type='parent', similarity_threshold=0.9):
    """
    Check for similar entity names within the DataFrame and allow the user to merge them.

    Args:
        df (DataFrame): The DataFrame to process.
        selected_fields (dict): Selected fields containing entity names.
        entity_type (str): The type of entity ('parent' or 'child').
        similarity_threshold (float): Threshold for considering names as similar.

    Returns:
        DataFrame: The DataFrame with entity names possibly merged.
        dict: A mapping of original names to merged names.

    Side Effects:
        Displays similar entity names and prompts user for action.
    """
    import itertools
    from entity_bridge.utils import calculate_similarity

    entity_name_field = selected_fields.get(f'{entity_type}_name')
    if not entity_name_field:
        return df, {}  # No entity names to compare

    st.subheader(f"Similar {entity_type.capitalize()} Names within the DataFrame")
    names = df[entity_name_field].dropna().unique()
    similar_pairs = []

    # Compute pairwise similarity
    for name_a, name_b in itertools.combinations(names, 2):
        similarity = calculate_similarity(name_a, name_b)
        if similarity >= similarity_threshold and name_a != name_b:
            similar_pairs.append({'NameA': name_a, 'NameB': name_b, 'Similarity': similarity})

    if not similar_pairs:
        st.write(f"No similar {entity_type} names found.")
        return df, {}

    similar_df = pd.DataFrame(similar_pairs)
    st.write("Found similar names:")
    st.dataframe(similar_df)

    # Create mappings based on user input
    name_mapping = {}
    for idx, row in similar_df.iterrows():
        name_a = row['NameA']
        name_b = row['NameB']
        similarity = row['Similarity']

        st.write(f"Do you want to merge '{name_a}' and '{name_b}'? (Similarity: {similarity:.2f})")
        action = st.radio(
            f"Action for '{name_a}' and '{name_b}':",
            options=['Merge', 'Keep Separate'],
            key=f'merge_{name_a}_{name_b}_{idx}'
        )
        if action == 'Merge':
            merged_name = st.text_input(
                f"Enter the merged name for '{name_a}' and '{name_b}':",
                value=name_a,
                key=f'merged_name__{name_a}_{name_b}_{idx}'
            )
            name_mapping[name_a] = merged_name
            name_mapping[name_b] = merged_name

    # Apply the mapping to the DataFrame
    if name_mapping:
        df[entity_name_field] = df[entity_name_field].replace(name_mapping)
        st.success(f"Merged names have been applied to the DataFrame.")
    else:
        st.info("No names were merged.")

    return df, name_mapping

def normalize_ids(df, selected_fields):
    """
    Normalize IDs in the DataFrame, generating new IDs if they are missing.

    Args:
        df (DataFrame): The DataFrame to process.
        selected_fields (dict): Dictionary containing field names:
            - 'parent_id': Parent ID field name.
            - 'parent_name': Parent Name field name.
            - 'child_id': Child ID field name (optional).
            - 'child_name': Child Name field name (optional).

    Returns:
        DataFrame: The DataFrame with normalized IDs.

    Side Effects:
        Logs actions taken during ID normalization.
    """
    actions_log = []

    # Normalize Parent IDs
    if selected_fields['parent_id']:
        parent_id_field = selected_fields['parent_id']
        if df[parent_id_field].isnull().any():
            df[parent_id_field] = df[parent_id_field].fillna(method='ffill')
            log_normalization_actions(actions_log, f"Filled missing Parent IDs in '{parent_id_field}' with forward fill.")
    else:
        # Generate unique Parent IDs based on Parent Names
        parent_name_field = selected_fields['parent_name']
        if df[parent_name_field].isnull().any():
            st.error(f"Missing values in '{parent_name_field}'. Cannot generate IDs for these entries.")
        df['generated_parent_id'] = df[parent_name_field].apply(lambda x: generate_unique_identifier())
        selected_fields['parent_id'] = 'generated_parent_id'
        log_normalization_actions(actions_log, "Generated unique Parent IDs based on Parent Names.")

    # Normalize Child IDs, if present
    if selected_fields.get('child_name'):
        child_name_field = selected_fields['child_name']
        if df[child_name_field].isnull().any():
            st.error(f"Missing values in '{child_name_field}'. Cannot generate IDs for these entries.")
        if selected_fields.get('child_id'):
            child_id_field = selected_fields['child_id']
            if df[child_id_field].isnull().any():
                df[child_id_field] = df[child_id_field].fillna(method='ffill')
                log_normalization_actions(actions_log, f"Filled missing Child IDs in '{child_id_field}' with forward fill.")
        else:
            # Generate unique Child IDs based on Child Names
            df['generated_child_id'] = df[child_name_field].apply(lambda x: generate_unique_identifier())
            selected_fields['child_id'] = 'generated_child_id'
            log_normalization_actions(actions_log, "Generated unique Child IDs based on Child Names.")
    else:
        # No Child Names provided; skip Child ID normalization
        pass

    # Display the normalization actions log
    if actions_log:
        st.subheader("ID Normalization Actions")
        for action in actions_log:
            st.write(f"- {action}")

    return df, selected_fields


def normalize_entity_names(df, selected_fields, parent_custom_stopwords=None, child_custom_stopwords=None):
    """
    Normalize entity names in the DataFrame by applying various text preprocessing steps.

    Args:
        df (DataFrame): The DataFrame to process.
        selected_fields (dict): Dictionary containing field names:
            - 'parent_name': Parent Name field name.
            - 'child_name': Child Name field name (optional).
        parent_custom_stopwords (list,optional): List of custom stopwords for parent names.
        child_custom_stopwords (list,optional): List of custom stopwords for child names.

    Returns:
        DataFrame: The DataFrame with normalized names.

    Side Effects:
        Adds new columns with normalized names and logs the normalization steps.
    """
    actions_log = []

    # Duplicate original Parent Name column
    parent_name_field = selected_fields['parent_name']
    df[f'{parent_name_field}_original'] = df[parent_name_field]
    log_normalization_actions(actions_log, f"Copied '{parent_name_field}' to '{parent_name_field}_original'.")

    # Normalize Parent Names
    df[parent_name_field] = df[parent_name_field].apply(
        lambda x: normalize_text(x, custom_stopwords=parent_custom_stopwords) if pd.notnull(x) else x
        )
    log_normalization_actions(actions_log, f"Normalized Parent Names in '{parent_name_field}'.")

    # If Child Names are present, normalize them
    if selected_fields.get('child_name'):
        child_name_field = selected_fields['child_name']
        df[f'{child_name_field}_original'] = df[child_name_field]
        log_normalization_actions(actions_log, f"Copied '{child_name_field}' to '{child_name_field}_original'.")

        df[child_name_field] = df[child_name_field].apply(
            lambda x: normalize_text(x, custom_stopwords=child_custom_stopwords) if pd.notnull(x) else x
            )
        log_normalization_actions(actions_log, f"Normalized Child Names in '{child_name_field}'.")

    # Display the normalization actions log
    if actions_log:
        st.subheader("Entity Name Normalization Actions")
        for action in actions_log:
            st.write(f"- {action}")

    return df

def normalize_data_frames(data_frames, parent_custom_stopwords=None, child_custom_stopwords=None):
    """
    Apply normalization to a list of DataFrames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).
        parent_custom_stopwords (list,optional): List of custom stopwords for parent names.
        child_custom_stopwords (list,optional): List of custom stopwords for child names.

    Returns:
        list: List of normalized DataFrames with updated selected_fields.

    Side Effects:
        Updates each DataFrame in the list and logs actions.
    """
    normalized_data_frames = []

    for idx, (df, selected_fields) in enumerate(data_frames):
        st.header(f"Normalizing DataFrame {idx + 1}")

        # Normalize IDs
        df, selected_fields = normalize_ids(df, selected_fields)

        # Normalize Entity Names
        df = normalize_entity_names(
            df,
            selected_fields,
            parent_custom_stopwords=parent_custom_stopwords,
            child_custom_stopwords=child_custom_stopwords)

        # Check and merge similar parent names
        df, parent_name_mapping = check_and_merge_similar_names(
            df, selected_fields, entity_type='parent'
        )
        # Optionally save parent_name_mapping if needed

        # Check and merge similar child names
        df, child_name_mapping = check_and_merge_similar_names(
            df, selected_fields, entity_type='child'
        )
        # Optionally save child_name_mapping if needed

        normalized_data_frames.append((df, selected_fields))

    return normalized_data_frames