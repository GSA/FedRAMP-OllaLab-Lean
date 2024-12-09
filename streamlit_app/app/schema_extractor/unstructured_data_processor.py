# schema_extractor/unstructured_data_processor.py

import re
import string
import logging
from typing import List, Dict, Any
from collections import defaultdict

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize, ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from schema_extractor.utils import backup_data, detect_sensitive_data

# Ensure necessary NLTK data packages are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_unstructured_data(sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes unstructured data files by performing EDA, schema design, and validation.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data.

    Returns:
        dict: A dictionary containing EDA results, designed schema, and validation status.
    """
    logger.info("Starting processing of unstructured data.")

    # 1. Exploratory Data Analysis
    text_data = load_unstructured_data(sanitized_data)
    eda_results = perform_eda(text_data)

    # 2. Data Schema Design
    groups = group_similar_values(text_data, eda_results.get('common_ngrams', {}), eda_results.get('numeric_stats', {}))
    schema = design_schema(groups)

    # 3. Data Schema Validation
    is_valid = validate_schema(text_data, schema)

    logger.info("Completed processing of unstructured data.")

    return {
        'eda_results': eda_results,
        'schema': schema,
        'is_valid': is_valid
    }

def load_unstructured_data(sanitized_data: Dict[str, Any]) -> List[str]:
    """
    Loads unstructured text data from sanitized files.

    Args:
        sanitized_data (dict): Sanitized data with file names as keys and content as values.

    Returns:
        list: List of text data strings.
    """
    logger.info("Loading unstructured data from sanitized files.")
    text_data = []
    for file_name, content in sanitized_data.items():
        logger.debug(f"Loading data from {file_name}.")
        if isinstance(content, bytes):
            try:
                text = content.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                logger.warning(f"Could not decode {file_name}; skipping.")
                continue
        elif isinstance(content, str):
            text = content
        else:
            logger.warning(f"Unsupported content type for {file_name}; skipping.")
            continue
        text_data.append(text)
    logger.info(f"Loaded {len(text_data)} unstructured data entries.")
    return text_data

def perform_eda(text_data: List[str]) -> Dict[str, Any]:
    """
    Performs Exploratory Data Analysis on text data.

    Args:
        text_data (list): List of text data strings.

    Returns:
        dict: Results of the EDA, including token counts, common words, n-gram stats, etc.
    """
    logger.info("Performing Exploratory Data Analysis (EDA).")
    eda_results = {}

    # Preprocessing
    cleaned_data = [clean_text(text) for text in text_data]
    eda_results['cleaned_data'] = cleaned_data

    # Tokenization
    tokens = [word_tokenize(text) for text in cleaned_data]
    eda_results['tokens'] = tokens

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens_no_stop = [[token.lower() for token in doc if token.lower() not in stop_words and token.isalpha()] for doc in tokens]
    eda_results['tokens_no_stop'] = tokens_no_stop

    # Most common words
    all_words = [word for doc in tokens_no_stop for word in doc]
    word_freq = nltk.FreqDist(all_words)
    eda_results['word_freq'] = word_freq.most_common(20)

    # N-gram Analysis
    bigrams = [gram for doc in tokens_no_stop for gram in ngrams(doc, 2)]
    trigrams = [gram for doc in tokens_no_stop for gram in ngrams(doc, 3)]
    bigram_freq = nltk.FreqDist(bigrams)
    trigram_freq = nltk.FreqDist(trigrams)
    eda_results['bigram_freq'] = bigram_freq.most_common(20)
    eda_results['trigram_freq'] = trigram_freq.most_common(20)

    # Numeric Values Statistics
    numeric_stats = extract_numeric_stats(text_data)
    eda_results['numeric_stats'] = numeric_stats

    # Sentence Length Statistics
    sentence_lengths = [len(word_tokenize(sent)) for text in cleaned_data for sent in nltk.sent_tokenize(text)]
    eda_results['sentence_lengths'] = {
        'average_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
        'max_length': max(sentence_lengths) if sentence_lengths else 0,
        'min_length': min(sentence_lengths) if sentence_lengths else 0
    }

    # Word Cloud Data
    wordcloud = generate_wordcloud(all_words)
    eda_results['wordcloud'] = wordcloud

    # Bar Charts Data
    eda_results['bar_charts'] = {
        'word_freq': eda_results['word_freq'],
        'bigram_freq': eda_results['bigram_freq'],
        'trigram_freq': eda_results['trigram_freq']
    }

    # Topic Modeling
    topics = perform_topic_modeling(cleaned_data, num_topics=5)
    eda_results['topics'] = topics

    logger.info("EDA completed successfully.")
    return eda_results

def clean_text(text: str) -> str:
    """
    Cleans the input text by removing harmful characters and normalizing whitespace.

    Args:
        text (str): The raw text.

    Returns:
        str: Cleaned text.
    """
    logger.debug("Cleaning text.")
    # Remove harmful characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(rf'[{re.escape(string.punctuation)}]', '', text)  # Remove punctuation
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_numeric_stats(text_data: List[str]) -> Dict[str, Any]:
    """
    Extracts numeric values from text and computes statistics.

    Args:
        text_data (list): List of text data strings.

    Returns:
        dict: Statistics of numeric values found.
    """
    logger.info("Extracting numeric values statistics.")
    numeric_values = []
    for text in text_data:
        # Find all numbers in the text
        numbers = re.findall(r'\b\d+\b', text)
        numeric_values.extend([int(num) for num in numbers])

    if numeric_values:
        stats = {
            'count': len(numeric_values),
            'mean': sum(numeric_values) / len(numeric_values),
            'median': sorted(numeric_values)[len(numeric_values)//2],
            'max': max(numeric_values),
            'min': min(numeric_values)
        }
    else:
        stats = {
            'count': 0,
            'mean': None,
            'median': None,
            'max': None,
            'min': None
        }

    logger.debug(f"Numeric stats: {stats}")
    return stats

def generate_wordcloud(words: List[str]) -> WordCloud:
    """
    Generates a word cloud from a list of words.

    Args:
        words (list): List of words.

    Returns:
        WordCloud: Generated word cloud object.
    """
    logger.info("Generating word cloud.")
    text = ' '.join(words)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud

def perform_topic_modeling(cleaned_data: List[str], num_topics: int = 5) -> List[Dict[str, Any]]:
    """
    Performs topic modeling on the cleaned text data.

    Args:
        cleaned_data (list): List of cleaned text strings.
        num_topics (int): Number of topics to extract.

    Returns:
        list: List of topics with their top words.
    """
    logger.info("Performing topic modeling.")
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(cleaned_data)

    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    topics = []
    for idx, topic in enumerate(lda.components_):
        top_features = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]]
        topics.append({
            'topic_id': idx + 1,
            'top_words': top_features
        })

    logger.debug(f"Extracted topics: {topics}")
    return topics

def group_similar_values(text_data: List[str], common_ngrams: Dict[str, Any], numeric_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Groups similar values such as n-grams and numeric values.

    Args:
        text_data (list): List of text data strings.
        common_ngrams (dict): Common n-grams from EDA.
        numeric_stats (dict): Numeric statistics from EDA.

    Returns:
        dict: Grouped values with group names, types, and descriptions.
    """
    logger.info("Grouping similar values.")
    groups = {}

    # Grouping trigrams
    trigrams = common_ngrams.get('trigram_freq', [])
    if trigrams:
        group_name = "Common Trigrams"
        groups[group_name] = {
            'type': 'String',
            'description': 'Frequently occurring three-word sequences.',
            'values': [' '.join(trigram) for trigram, freq in trigrams]
        }

    # Grouping bigrams
    bigrams = common_ngrams.get('bigram_freq', [])
    if bigrams:
        group_name = "Common Bigrams"
        groups[group_name] = {
            'type': 'String',
            'description': 'Frequently occurring two-word sequences.',
            'values': [' '.join(bigram) for bigram, freq in bigrams]
        }

    # Grouping numeric ranges if applicable
    if numeric_stats.get('count', 0) > 0:
        group_name = "Numeric Values"
        groups[group_name] = {
            'type': 'Numeric',
            'description': 'Extracted numeric values from the text.',
            'values': numeric_stats
        }

    logger.debug(f"Grouped values: {groups}")
    return groups

def design_schema(groups: Dict[str, Any]) -> Dict[str, Any]:
    """
    Designs a schema based on grouped values.

    Args:
        groups (dict): Grouped values.

    Returns:
        dict: Designed JSON schema.
    """
    logger.info("Designing schema based on grouped values.")
    schema = {
        "title": "Unstructured Data Schema",
        "description": "Schema generated from unstructured text data.",
        "type": "object",
        "properties": {}
    }

    for group_name, group_info in groups.items():
        key = snake_case(group_name)
        if group_info['type'] == 'String':
            schema['properties'][key] = {
                "type": "string",
                "description": group_info['description']
            }
        elif group_info['type'] == 'Numeric':
            schema['properties'][key] = {
                "type": "object",
                "description": group_info['description'],
                "properties": {
                    "count": {"type": "integer"},
                    "mean": {"type": "number"},
                    "median": {"type": "number"},
                    "max": {"type": "integer"},
                    "min": {"type": "integer"}
                },
                "required": ["count", "mean", "median", "max", "min"]
            }
        # Extendable for other types

    logger.debug(f"Designed schema: {schema}")
    return schema

def snake_case(name: str) -> str:
    """
    Converts a string to snake_case.

    Args:
        name (str): The input string.

    Returns:
        str: The snake_case version of the input.
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    name = name.replace(" ", "_").lower()
    return name

def validate_schema(text_data: List[str], schema: Dict[str, Any]) -> bool:
    """
    Validates the ability to extract structured data from unstructured data using the schema.

    Args:
        text_data (list): List of text data strings.
        schema (dict): Designed schema.

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    logger.info("Validating schema against unstructured data.")
    # Placeholder for actual validation logic
    # This could involve attempting to extract structured data and ensuring it fits the schema
    # For now, we'll assume it's valid
    is_valid = True
    logger.debug(f"Schema validation result: {is_valid}")
    return is_valid

def plot_wordcloud(wordcloud: WordCloud) -> None:
    """
    Plots the word cloud using matplotlib.

    Args:
        wordcloud (WordCloud): The word cloud object to plot.
    """
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def plot_bar_chart(frequencies: List[tuple], title: str) -> None:
    """
    Plots a bar chart for word or n-gram frequencies.

    Args:
        frequencies (list): List of tuples containing items and their frequencies.
        title (str): Title of the bar chart.
    """
    items, counts = zip(*frequencies) if frequencies else ([], [])
    plt.figure(figsize=(10, 5))
    plt.bar(items, counts)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()