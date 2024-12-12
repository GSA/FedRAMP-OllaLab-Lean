# streamlit_app/app/entity_bridge/duplicate_remover.py

"""
Duplicate Remover Module

This module provides functions to identify and remove duplicate rows from DataFrames.
"""

import pandas as pd
import streamlit as st
from entity_bridge.utils import log_normalization_actions

def identify_duplicates(df, selected_fields):
    """
    Identify duplicate rows in the DataFrame based on combinations of normalized fields.

    Args:
        df (DataFrame): The DataFrame to check for duplicates.
        selected_fields (dict): Dictionary containing field names:
            - 'parent_id': Parent ID field name.
            - 'parent_name': Parent Name field name.
            - 'child_id': Child ID field name (optional).
            - 'child_name': Child Name field name (optional).

    Returns:
        DataFrame: A DataFrame containing duplicate rows.

    Side Effects:
        Logs the number of duplicates found and displays them.
    """
    # Prepare list of columns to consider
    columns_to_check = []
    if selected_fields.get('parent_id'):
        columns_to_check.append(selected_fields['parent_id'])
    if selected_fields.get('parent_name'):
        columns_to_check.append(selected_fields['parent_name'])
    if selected_fields.get('child_id'):
        columns_to_check.append(selected_fields['child_id'])
    if selected_fields.get('child_name'):
        columns_to_check.append(selected_fields['child_name'])

    # Identify duplicates
    duplicated_rows = df[df.duplicated(subset=columns_to_check, keep=False)]

    num_duplicates = len(duplicated_rows)
    if num_duplicates > 0:
        st.write(f"Found {num_duplicates} duplicate rows based on fields {columns_to_check}:")
        st.dataframe(duplicated_rows)
    else:
        st.write("No duplicate rows found.")

    return duplicated_rows

def remove_duplicates(df, selected_fields):
    """
    Remove duplicate rows from the DataFrame based on combinations of normalized fields.

    Args:
        df (DataFrame): The DataFrame to process.
        selected_fields (dict): Dictionary containing field names.

    Returns:
        DataFrame: The DataFrame after removing duplicates.

    Side Effects:
        Logs the action of removing duplicates and displays removed rows.
    """
    actions_log = []
    # Prepare list of columns to consider
    columns_to_check = []
    if selected_fields.get('parent_id'):
        columns_to_check.append(selected_fields['parent_id'])
    if selected_fields.get('parent_name'):
        columns_to_check.append(selected_fields['parent_name'])
    if selected_fields.get('child_id'):
        columns_to_check.append(selected_fields['child_id'])
    if selected_fields.get('child_name'):
        columns_to_check.append(selected_fields['child_name'])

    # Identify duplicates
    duplicates = df[df.duplicated(subset=columns_to_check, keep=False)]

    if not duplicates.empty:
        st.write(f"Removing the following duplicate rows:")
        st.dataframe(duplicates)

    # Remove duplicates
    df_no_duplicates = df.drop_duplicates(subset=columns_to_check, keep='first')

    num_duplicates_removed = len(df) - len(df_no_duplicates) // 2  # Since keep='first', half of the duplicates are removed
    if num_duplicates_removed > 0:
        log_normalization_actions(actions_log, f"Removed {num_duplicates_removed} duplicate rows based on fields {columns_to_check}")
        st.write(f"Removed {num_duplicates_removed} duplicate rows.")
    else:
        st.write("No duplicates to remove.")

    return df_no_duplicates

def remove_duplicates_from_data_frames(data_frames):
    """
    Remove duplicates from a list of DataFrames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).

    Returns:
        list: List of DataFrames after duplicates have been removed.

    Side Effects:
        Updates each DataFrame in the list and logs actions.
    """
    deduplicated_data_frames = []
    for idx, (df, selected_fields) in enumerate(data_frames):
        st.header(f"Removing duplicates from DataFrame {idx + 1}")

        # Identify duplicates
        duplicates = identify_duplicates(df, selected_fields)
        # Remove duplicates
        df_no_duplicates = remove_duplicates(df, selected_fields)

        deduplicated_data_frames.append((df_no_duplicates, selected_fields))
    return deduplicated_data_frames