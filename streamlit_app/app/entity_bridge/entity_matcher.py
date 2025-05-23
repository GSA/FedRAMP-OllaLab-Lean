# streamlit_app/app/entity_bridge/entity_matcher.py

"""
Entity Matcher Module

This module provides functions to match entities across datasets using
similarity metrics and user input for ambiguous cases.
"""

import pandas as pd
import streamlit as st
from entity_bridge.utils import calculate_similarity, generate_unique_identifier
from collections import defaultdict


def compute_similarity_scores(df_list, column_name):
    """
    Compute similarity scores between entities across multiple DataFrames and display matches.

    Args:
        df_list (list): List of tuples (DataFrame, selected_fields).
        column_name (str): The key in selected_fields dict for the column containing the entities.

    Returns:
        DataFrame: A DataFrame containing pairs of entities and their similarity scores.

    Side Effects:
        Displays progress and matched results in the Streamlit UI.
    """
    from itertools import product
    similarity_scores = []
    total_comparisons = 0

    # Prepare data
    entities_per_df = []
    for df, selected_fields in df_list:
        entity_field_name = selected_fields.get(column_name)
        if entity_field_name:
            entities = df[entity_field_name].dropna().unique()
            entities_per_df.append(entities)
        else:
            entities_per_df.append([])

    # Compute total number of comparisons
    for i in range(len(entities_per_df)):
        for j in range(i+1, len(entities_per_df)):
            total_comparisons += len(entities_per_df[i]) * len(entities_per_df[j])

    progress = 0
    progress_bar = st.progress(0)

    # Compute similarity scores and collect matches
    for i in range(len(entities_per_df)):
        for j in range(i+1, len(entities_per_df)):
            for entity_a, entity_b in product(entities_per_df[i], entities_per_df[j]):
                score = calculate_similarity(entity_a, entity_b)
                similarity_scores.append({
                    'EntityA': entity_a,
                    'EntityB': entity_b,
                    'DataFrameA': i,
                    'DataFrameB': j,
                    'SimilarityScore': score
                })
                progress += 1
                if progress % 100 == 0 or progress == total_comparisons:
                    progress_bar.progress(progress / total_comparisons)

    similarity_df = pd.DataFrame(similarity_scores)

    # Display matched results above a certain threshold
    threshold = st.slider(
        "Set similarity score threshold for displaying matched results:",
        min_value=0.0, max_value=1.0, value=0.9, step=0.01,
        key=f'similarity_threshold_{column_name}'
    )
    matched_results = similarity_df[similarity_df['SimilarityScore'] >= threshold]
    st.write(f"Entities matched with similarity score >= {threshold}:")
    st.dataframe(matched_results.reset_index(drop=True))

    return similarity_df

def automated_entity_matching(similarity_df, threshold):
    """
    Automatically match entities based on a similarity threshold.

    Args:
        similarity_df (DataFrame): DataFrame containing pairs of entities and their similarity scores.
        threshold (float): Similarity threshold for automatic matching.

    Returns:
        dict: A dictionary mapping an entity to its group identifier.

    Side Effects:
        None.
    """
    # Initialize a dictionary to hold groups of matched entities
    entity_groups = {}
    group_id = 0

    # Sort similarity_df by similarity score in descending order
    similarity_df = similarity_df.sort_values(by='SimilarityScore', ascending=False).reset_index(drop=True)

    # Iterate through the similarity dataframe and group entities
    for idx, row in similarity_df.iterrows():
        entity_a = row['EntityA']
        entity_b = row['EntityB']
        score = row['SimilarityScore']

        if score >= threshold:
            # Check if either entity is already in a group
            group_a = entity_groups.get(entity_a)
            group_b = entity_groups.get(entity_b)

            if group_a and group_b:
                # Merge groups if different
                if group_a != group_b:
                    for key, value in entity_groups.items():
                        if value == group_b:
                            entity_groups[key] = group_a
            elif group_a:
                entity_groups[entity_b] = group_a
            elif group_b:
                entity_groups[entity_a] = group_b
            else:
                # Create a new group
                entity_groups[entity_a] = group_id
                entity_groups[entity_b] = group_id
                group_id += 1
        else:
            # Stop processing further as scores are sorted in descending order
            break

    # Assign unique group IDs to entities not in any group
    for entity in set(similarity_df['EntityA']).union(set(similarity_df['EntityB'])):
        if entity not in entity_groups:
            entity_groups[entity] = group_id
            group_id += 1

    return entity_groups


def user_confirm_ambiguous_matches(ambiguous_matches):
    """
    Present ambiguous matches to the user for confirmation.

    Args:
        ambiguous_matches (DataFrame): DataFrame containing ambiguous entity matches.

    Returns:
        dict: A dictionary with user-confirmed entity groupings.

    Side Effects:
        Displays prompts in the Streamlit UI for user interaction.
    """
    st.write("Please review the following ambiguous matches:")

    user_confirmed_groups = {}
    group_id = max(ambiguous_matches['GroupID'].unique()) + 1

    for idx, row in ambiguous_matches.iterrows():
        entity_a = row['EntityA']
        entity_b = row['EntityB']
        score = row['SimilarityScore']

        st.write(f"Do these entities represent the same entity?")
        st.write(f"- Entity A: {entity_a}")
        st.write(f"- Entity B: {entity_b}")
        st.write(f"Similarity Score: {score:.2f}")

        response = st.radio(
            "Select an option:",
            options=['Yes, same entity', 'No, different entities'],
            key=f'ambiguous_match_{idx}'
        )

        if response == 'Yes, same entity':
            # Assign to the same group
            group = user_confirmed_groups.get(entity_a) or user_confirmed_groups.get(entity_b) or group_id
            user_confirmed_groups[entity_a] = group
            user_confirmed_groups[entity_b] = group
            group_id += 1
        else:
            # Assign different groups if not already assigned
            if entity_a not in user_confirmed_groups:
                user_confirmed_groups[entity_a] = group_id
                group_id += 1
            if entity_b not in user_confirmed_groups:
                user_confirmed_groups[entity_b] = group_id
                group_id += 1

    return user_confirmed_groups


def construct_unique_entity_list(data_frames, entity_type='parent'):
    """
    Construct a unique entity list (either parent or child) from the data frames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).
        entity_type (str): Type of entity to process ('parent' or 'child').

    Returns:
        DataFrame: DataFrame containing unique entities with unique identifiers.

    Side Effects:
        Displays progress in the Streamlit UI.
    """
    st.write(f"Constructing unique {entity_type} entity list...")

    # Collect unique entities from all data frames
    unique_entities = set()
    for df, selected_fields in data_frames:
        entity_field = selected_fields[f'{entity_type}_name']
        unique_entities.update(df[entity_field].unique())

    unique_entities = list(unique_entities)

    # Initialize a DataFrame to store entity information
    entity_df = pd.DataFrame({f'{entity_type}_name': unique_entities})

    # Assign unique identifiers
    entity_df[f'Unique{entity_type.capitalize()}ID'] = [generate_unique_identifier() for _ in unique_entities]

    return entity_df


def enrich_data_frames_with_unique_ids(data_frames, unique_entities_df, entity_type='parent'):
    """
    Enrich the original data frames with unique entity IDs.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).
        unique_entities_df (DataFrame): DataFrame containing unique entities and their identifiers.
        entity_type (str): Type of entity to process ('parent' or 'child').

    Returns:
        list: List of enriched DataFrames.

    Side Effects:
        Updates the DataFrames in place.
    """
    st.write(f"Enriching data frames with unique {entity_type} IDs...")
    enriched_data_frames = []

    for idx, (df, selected_fields) in enumerate(data_frames):
        entity_field = selected_fields[f'{entity_type}_name']
        df_enriched = df.merge(
            unique_entities_df,
            left_on=entity_field,
            right_on=f'{entity_type}_name',
            how='left'
        )

        # Drop the extra entity name column from the merge
        df_enriched = df_enriched.drop(columns=[f'{entity_type}_name_y'])
        df_enriched = df_enriched.rename(columns={f'{entity_type}_name_x': f'{entity_type}_name'})

        enriched_data_frames.append(df_enriched)

    return enriched_data_frames


def construct_unique_parent_list(data_frames):
    """
    Construct a unique parent entity list from the data frames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).

    Returns:
        DataFrame: DataFrame containing unique parent entities with unique identifiers.

    Side Effects:
        None.
    """
    # Compute similarity scores between parent entities
    similarity_df = compute_similarity_scores(data_frames, 'parent_name')

    # Set similarity threshold for automated matching
    similarity_threshold = st.slider(
        "Set similarity threshold for parent entity matching:",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.01
    )

    # Perform automated entity matching
    entity_groups = automated_entity_matching(similarity_df, similarity_threshold)

    # Construct the unique parent entity DataFrame
    unique_parents = []
    group_to_entities = defaultdict(list)

    for entity, group in entity_groups.items():
        group_to_entities[group].append(entity)

    for group, entities in group_to_entities.items():
        unique_id = generate_unique_identifier()
        for entity in entities:
            unique_parents.append({
                'ParentName': entity,
                'UniqueParentID': unique_id
            })

    # Create DataFrame from the list of unique parents
    unique_parents_df = pd.DataFrame(unique_parents)

    return unique_parents_df


def construct_unique_child_list(data_frames):
    """
    Construct a unique child entity list from the data frames.

    Args:
        data_frames (list): List of tuples (DataFrame, selected_fields).

    Returns:
        DataFrame: DataFrame containing unique child entities with unique identifiers.

    Side Effects:
        None.
    """
    # Identify if child names are present
    child_names_present = any(selected_fields.get('child_name') for _, selected_fields in data_frames)
    if not child_names_present:
        st.write("No child names provided in the datasets.")
        return pd.DataFrame(columns=['ChildName', 'UniqueChildID'])

    # Compute similarity scores between child entities
    similarity_df = compute_similarity_scores(data_frames, 'child_name')

    # Set similarity threshold for automated matching
    similarity_threshold = st.slider(
        "Set similarity threshold for child entity matching:",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.01
    )

    # Perform automated entity matching
    entity_groups = automated_entity_matching(similarity_df, similarity_threshold)

    # Construct the unique child entity DataFrame
    unique_children = []
    group_to_entities = defaultdict(list)

    for entity, group in entity_groups.items():
        group_to_entities[group].append(entity)

    for group, entities in group_to_entities.items():
        unique_id = generate_unique_identifier()
        for entity in entities:
            unique_children.append({
                'ChildName': entity,
                'UniqueChildID': unique_id
            })

    # Create DataFrame from the list of unique children
    unique_children_df = pd.DataFrame(unique_children)

    return unique_children_df
