# schema_extractor/unstructured_data_processor.py

import streamlit as st
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd

from schema_extractor import utils
from schema_extractor import ui_components

# Ensure necessary NLTK data packages are downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def process_unstructured_data(sanitized_data):
    """
    Processes unstructured data files.

    Performs EDA, data schema design, and validation.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data.
    """
    # Exploratory Data Analysis
    text_data = load_unstructured_data(sanitized_data)
    perform_eda(text_data)

    # Data Schema Design
    groups = group_similar_values(text_data)
    schema = design_schema(groups)

    # Data Schema Validation
    validate_schema(text_data, schema)

def load_unstructured_data(sanitized_data):
    """
    Loads unstructured text data.

    Args:
        sanitized_data (dict): Sanitized data.

    Returns:
        list: List of text data strings.
    """
    text_data = []
    for file_name, content in sanitized_data.items():
        # Assuming content is a string
        text_data.append(content)
    return text_data

def perform_eda(text_data):
    """
    Performs Exploratory Data Analysis on text data.

    Args:
        text_data (list): List of text data strings.
    """
    st.header("Exploratory Data Analysis")

    # Ask the user for a list of stopwords
    user_stopwords = ui_components.get_user_stopwords()
    default_stopwords = set(stopwords.words('english'))
    stop_words = default_stopwords.union(user_stopwords)

    # Concatenate all text data
    full_text = ' '.join(text_data)

    # Remove unusual/harmful characters
    sanitized_text = utils.remove_unusual_characters(full_text)

    # Normalize text: lowercase and remove extra whitespaces
    normalized_text = sanitized_text.lower()
    normalized_text = re.sub(r'\s+', ' ', normalized_text)

    # Tokenize text
    tokens = word_tokenize(normalized_text)

    # Remove stopwords and non-alphabetic tokens
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    # Report the number of tokens
    st.write(f"Total number of tokens after preprocessing: {len(tokens)}")

    # Identify and report the most common words
    word_counts = Counter(tokens)
    most_common_words = word_counts.most_common(20)
    st.subheader("Most Common Words")
    st.table(pd.DataFrame(most_common_words, columns=['Word', 'Frequency']))

    # Perform n-gram analysis
    ngrams_list = get_ngrams(tokens)
    # Identify and report the values and related statistics of bigrams and trigrams
    st.subheader("N-Gram Analysis")
    for n in ngrams_list:
        st.write(f"Top 10 Most Common {n}-grams")
        ngram_counts = ngrams_list[n]
        common_ngrams = ngram_counts.most_common(10)
        formatted_ngrams = [(' '.join(gram), count) for gram, count in common_ngrams]
        st.table(pd.DataFrame(formatted_ngrams, columns=[f'{n}-gram', 'Frequency']))

    # Identify and report the values and related statistics of numeric values
    numeric_values = extract_numeric_values(normalized_text)
    st.subheader("Numeric Values Analysis")
    if numeric_values:
        st.write(f"Total numeric values found: {len(numeric_values)}")
        st.write(f"Statistics:")
        st.write(pd.Series(numeric_values).describe())
    else:
        st.write("No numeric values found.")

    # Calculate and report statistics on sentence lengths
    sentences = sent_tokenize(sanitized_text)
    sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
    st.subheader("Sentence Length Analysis")
    st.write(f"Number of sentences: {len(sentences)}")
    st.write("Sentence length statistics:")
    st.write(pd.Series(sentence_lengths).describe())

    # Display wordcloud
    st.subheader("Wordcloud")
    wordcloud_image = generate_wordcloud(tokens)
    st.image(wordcloud_image)

    # Display bar charts for word frequencies
    st.subheader("Word Frequencies Bar Chart")
    fig, ax = plt.subplots()
    words, counts = zip(*most_common_words)
    ax.bar(words, counts)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # Automatically discover topics and sub-topics within the texts
    st.subheader("Topic Modeling")
    topics = perform_topic_modeling(tokens)
    st.write("Identified Topics:")
    for idx, topic in enumerate(topics):
        st.write(f"Topic {idx+1}: {', '.join(topic)}")

def extract_numeric_values(text):
    """
    Extracts numeric values from the text.

    Args:
        text (str): The text from which to extract numeric values.

    Returns:
        list: List of numeric values as floats.
    """
    numeric_strings = re.findall(r'\b\d+\.?\d*\b', text)
    numeric_values = [float(num) for num in numeric_strings]
    return numeric_values

def get_ngrams(tokens):
    """
    Generates n-grams (bigrams and trigrams) from tokens.

    Args:
        tokens (list): List of tokens.

    Returns:
        dict: Dictionary containing Counter objects for bigrams and trigrams.
    """
    from nltk.util import ngrams

    ngrams_list = {}
    for n in [2, 3]:
        n_grams = ngrams(tokens, n)
        ngram_counts = Counter(n_grams)
        ngrams_list[n] = ngram_counts
    return ngrams_list

def generate_wordcloud(tokens):
    """
    Generates a wordcloud image from tokens.

    Args:
        tokens (list): List of tokens.

    Returns:
        matplotlib.figure.Figure: Wordcloud image.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens))

    fig = plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    return fig

def perform_topic_modeling(tokens):
    """
    Performs topic modeling on tokens.

    Args:
        tokens (list): List of tokens.

    Returns:
        list: List of topics, each topic is a list of words.
    """
    from gensim import corpora, models

    # Create a dictionary representation of the documents.
    dictionary = corpora.Dictionary([tokens])

    # Create a corpus: Term Document Frequency
    corpus = [dictionary.doc2bow(tokens)]

    # Number of topics
    num_topics = 3  # You can adjust the number of topics

    # Build LDA model
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)

    # Extract topics
    topics = []
    for idx in range(num_topics):
        topic = lda_model.show_topic(idx, topn=5)
        topic_words = [word for word, prob in topic]
        topics.append(topic_words)
    return topics

def group_similar_values(text_data):
    """
    Groups similar values such as n-grams and numeric values.

    Args:
        text_data (list): List of text data strings.

    Returns:
        dict: Grouped values.
    """
    st.header("Group Similar Values")

    # Collect n-grams and numeric values from text data
    tokens = []
    numeric_values = []
    for text in text_data:
        tokens.extend(word_tokenize(text.lower()))
        numeric_values.extend(extract_numeric_values(text))

    # Generate bigrams and trigrams
    bigrams = list(nltk.bigrams(tokens))
    trigrams = list(nltk.trigrams(tokens))

    # Remove stopwords and non-alphabetic tokens from n-grams
    stop_words = set(stopwords.words('english'))
    bigrams = [gram for gram in bigrams if all(word.isalpha() and word not in stop_words for word in gram)]
    trigrams = [gram for gram in trigrams if all(word.isalpha() and word not in stop_words for word in gram)]

    # User interface to create groups
    groups = ui_components.group_values_interface(bigrams, trigrams, numeric_values)
    return groups

def design_schema(groups):
    """
    Designs a schema based on grouped values.

    Args:
        groups (dict): Grouped values.

    Returns:
        dict: Designed schema.
    """
    st.header("Design Schema")
    schema = ui_components.schema_builder_interface_unstructured(groups)
    return schema

def validate_schema(text_data, schema):
    """
    Validates the ability to extract structured data from unstructured text using the schema.

    Args:
        text_data (list): List of text data strings.
        schema (dict): Designed schema.
    """
    st.header("Schema Validation")

    # Apply the schema to extract data
    extracted_data = []
    for text in text_data:
        data = extract_data_using_schema(text, schema)
        extracted_data.append(data)

    # Check if data extraction was successful
    if all(extracted_data):
        st.success("Schema validation successful. Structured data extracted.")
        st.write("Extracted Data Preview:")
        st.write(pd.DataFrame(extracted_data))
    else:
        st.error("Schema validation failed. Unable to extract structured data from all texts.")

def extract_data_using_schema(text, schema):
    """
    Extracts data from text using the given schema.

    Args:
        text (str): The text from which to extract data.
        schema (dict): The schema to use for data extraction.

    Returns:
        dict: Extracted data.
    """
    # Placeholder for actual data extraction logic
    # Implement extraction based on schema definitions
    # For simplicity, we'll return an empty dict
    extracted_data = {}

    # Example (pseudo-code):
    # for property_name, property_info in schema['properties'].items():
    #     if property_info['type'] == 'string':
    #         # Use regex or NLP techniques to extract string data
    #     elif property_info['type'] == 'number':
    #         # Extract numeric values
    #     # and so on...

    return extracted_data