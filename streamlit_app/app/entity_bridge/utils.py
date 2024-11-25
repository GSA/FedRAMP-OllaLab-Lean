# streamlit_app/app/entity_bridge/utils.py

"""
Utilities Module

This module contains utility functions used throughout the Entity Bridge application.
"""

import uuid
import re
import string
from difflib import SequenceMatcher

# Optional: Import NLTK for stopword removal
try:
    from nltk.corpus import stopwords
    from nltk import download as nltk_download
    STOPWORDS = set(stopwords.words('english'))
except (ImportError, LookupError):
    STOPWORDS = set()
    # If NLTK stopwords are not available, define a default list
    DEFAULT_STOPWORDS = {
        'INC', 'LLC', 'CORP', 'CO', 'LIMITED', 'COMPANY', 'THE', 'AND', 'OF',
        'IN', 'ON', 'FOR', 'BY', 'AT', 'WITH'
    }
    STOPWORDS = DEFAULT_STOPWORDS
    print("NLTK stopwords not available. Using default stopwords.")


def generate_unique_identifier():
    """
    Generate a unique identifier string using UUID4.

    Returns:
        str: A UUID4 string, e.g., 'f47ac10b-58cc-4372-a567-0e02b2c3d479'.
    """
    unique_id = str(uuid.uuid4())
    return unique_id


def calculate_similarity(s1, s2):
    """
    Calculate the similarity between two strings using sequence matching.

    Args:
        s1 (str): The first string to compare.
        s2 (str): The second string to compare.

    Returns:
        float: A similarity score between 0.0 and 1.0, where 1.0 means identical strings.

    Raises:
        TypeError: If either s1 or s2 is not a string.
    """
    if not isinstance(s1, str) or not isinstance(s2, str):
        raise TypeError("Both inputs must be strings.")

    similarity_score = SequenceMatcher(None, s1, s2).ratio()
    return similarity_score


def normalize_text(text, custom_stopwords=None):
    """
    Normalize text by converting to uppercase, removing punctuation, and eliminating stopwords.

    Args:
        text (str): The text to normalize.
        custom_stopwords (list, optional): A list of additional stopwords to remove.

    Returns:
        str: The normalized text.

    Raises:
        TypeError: If the input text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    # Convert to uppercase
    normalized = text.upper()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    normalized = normalized.translate(translator)
    
    # Split into words
    words = normalized.split()
    
    # Remove stopwords
    if custom_stopwords:
        combined_stopwords = STOPWORDS.union(set(word.upper() for word in custom_stopwords))
    else:
        combined_stopwords = STOPWORDS
    
    filtered_words = [word for word in words if word not in combined_stopwords]
    
    # Join back into a single string
    normalized = ' '.join(filtered_words)
    
    return normalized


def log_normalization_actions(actions_log, action_description):
    """
    Record a normalization action to the actions log.

    Args:
        actions_log (list): List maintaining logs of normalization actions.
        action_description (str): Description of the normalization action performed.

    Raises:
        TypeError: If actions_log is not a list or action_description is not a string.
    """
    if not isinstance(actions_log, list):
        raise TypeError("actions_log must be a list.")
    if not isinstance(action_description, str):
        raise TypeError("action_description must be a string.")
    
    actions_log.append(action_description)
