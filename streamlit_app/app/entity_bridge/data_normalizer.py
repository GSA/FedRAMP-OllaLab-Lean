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
    log_normalization_actions
)

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
        df['generated_parent_id'] = df[parent_name_field].apply(lambda x: generate_unique_identifier())
        selected_fields['parent_id'] = 'generated_parent_id'
        log_normalization_actions(actions_log, "Generated unique Parent IDs based on Parent Names.")

    # Normalize Child IDs, if present
    if selected_fields.get('child_name'):
        child_name_field = selected_fields['child_name']
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


def normalize_entity_names(df, selected_fields, custom_stopwords=None):
    """
    Normalize entity names in the DataFrame by applying various text preprocessing steps.

    Args:
        df (DataFrame): The DataFrame to process.
        selected_fields (dict): Dictionary containing field names:
            - 'parent_name': Parent Name field name.
            - 'child_name': Child Name field name (optional).
        custom_stopwords (list, optional): List of custom stopwords to remove from names.

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
    df[parent_name_field] = df[parent_name_field].apply(lambda x: normalize_text(x, custom_stopwords))
    log_normalization_actions(actions_log, f"Normalized Parent Names in '{parent_name_field}'.")

    # If Child Names are present, normalize them
    if selected_fields.get('child_name'):
        child_name_field = selected_fields['child_name']
        df[f'{child_name_field}_original'] = df[child_name_field]
        log_normalization_actions(actions_log, f"Copied '{child_name_field}' to '{child_name_field}_original'.")

        df[child_name_field] = df[child_name_field].apply(lambda x: normalize_text(x, custom_stopwords))
        log_normalization_actions(actions_log, f"Normalized Child Names in '{child_name_field}'.")

    # Display the normalization actions log
    if actions_log:
        st.subheader("Entity Name Normalization Actions")
        for action in actions_log:
            st.write(f"- {action}")

    return df


def normalize_data_frames(data_frames, custom_stopwords=None):
    """
    Apply normalization to a list of DataFrames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).
        custom_stopwords (list, optional): List of custom stopwords to remove from names.

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
        df = normalize_entity_names(df, selected_fields, custom_stopwords)

        normalized_data_frames.append((df, selected_fields))

    return normalized_data_frames