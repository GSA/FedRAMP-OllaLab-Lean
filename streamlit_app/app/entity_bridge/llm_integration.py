# streamlit_app/app/entity_bridge/llm_integration.py

"""
LLM Integration Module

This module provides functions to integrate with various Large Language Models (LLMs)
such as OpenAI, Ollama, Anthropic, Google Vertex AI, and AWS Bedrock.
"""

import os
import logging
from typing import Any, Dict

# Import necessary clients or SDKs for each provider
# Note: Users must install the required SDKs for each provider they intend to use.

# OpenAI
try:
    import openai
except ImportError:
    openai = None

# Anthropic
try:
    import anthropic
except ImportError:
    anthropic = None

# Google Vertex AI
try:
    from google.cloud import aiplatform
except ImportError:
    aiplatform = None

# AWS Bedrock (Note: AWS SDK supports Bedrock in later versions)
try:
    import boto3
except ImportError:
    boto3 = None

# Ollama (Assuming a hypothetical client, as Ollama is an open-source model runner)
# In practice, users would need to implement their own client or use an existing one.
# For demonstration purposes, we'll define a placeholder.
class OllamaClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def generate(self, prompt):
        # Placeholder method to call Ollama API
        pass


def setup_llm_client(provider: str, **credentials) -> Any:
    """
    Set up the LLM client based on the selected provider and credentials.

    Args:
        provider (str): The name of the LLM provider ('ollama', 'openai', 'anthropic', 'vertexai', 'bedrock').
        **credentials: Keyword arguments containing necessary credentials.

    Returns:
        object: An instance of the LLM client.

    Raises:
        ValueError: If the provider is unsupported or credentials are missing.
    """
    if provider.lower() == 'openai':
        if openai is None:
            raise ImportError("OpenAI library is not installed. Please install it with 'pip install openai'.")
        api_key = credentials.get('api_key')
        if not api_key:
            raise ValueError("API key is required for OpenAI.")
        openai.api_key = api_key
        return openai
    elif provider.lower() == 'anthropic':
        if anthropic is None:
            raise ImportError("Anthropic library is not installed. Please install it with 'pip install anthropic'.")
        api_key = credentials.get('api_key')
        if not api_key:
            raise ValueError("API key is required for Anthropic.")
        client = anthropic.Client(api_key=api_key)
        return client
    elif provider.lower() == 'vertexai':
        if aiplatform is None:
            raise ImportError("Google Cloud AI Platform library is not installed. Please install it with 'pip install google-cloud-aiplatform'.")
        # For Vertex AI, authentication is typically handled via environment variables or service accounts.
        aiplatform.init()
        return aiplatform
    elif provider.lower() == 'bedrock':
        if boto3 is None:
            raise ImportError("Boto3 library is not installed. Please install it with 'pip install boto3'.")
        # AWS credentials are typically handled via environment variables or configuration files.
        client = boto3.client('bedrock')
        return client
    elif provider.lower() == 'ollama':
        base_url = credentials.get('base_url', 'http://localhost:11434')
        client = OllamaClient(base_url=base_url)
        return client
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def generate_entity_mappings_with_llm(prompt: str, client: Any, provider: str, model_name: str) -> Dict[str, Any]:
    """
    Generate entity mappings using the provided LLM client.

    Args:
        prompt (str): The prompt to send to the LLM.
        client (object): The LLM client instance.
        provider (str): The name of the LLM provider.
        model_name (str): The name of the LLM model to use.

    Returns:
        dict: A dictionary containing the entity mappings generated by the LLM.

    Raises:
        Exception: If the LLM generation fails.
    """
    try:
        if provider.lower() == 'openai':
            # For OpenAI, using ChatCompletion API
            response = client.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.7,
            )
            generated_text = response.choices[0].message['content'].strip()
            # Parse the generated_text into a dictionary as needed
            entity_mappings = parse_llm_output(generated_text)
            return entity_mappings
        elif provider.lower() == 'anthropic':
            # For Anthropic's Claude API
            response = client.completion(
                prompt=prompt,
                model=model_name,
                max_tokens_to_sample=500,
                stop_sequences=[],
                temperature=0.7,
            )
            generated_text = response.get('completion', '').strip()
            entity_mappings = parse_llm_output(generated_text)
            return entity_mappings
        elif provider.lower() == 'vertexai':
            # For Google Vertex AI
            # Assuming use of Text Generation models
            model = client.TextGenerationModel.from_pretrained(model_name)
            response = model.predict(prompt)
            generated_text = response.text.strip()
            entity_mappings = parse_llm_output(generated_text)
            return entity_mappings
        elif provider.lower() == 'bedrock':
            # For AWS Bedrock
            response = client.generate_text(
                modelId=model_name,
                prompt=prompt,
                # Other parameters as needed
            )
            generated_text = response.get('result', '').strip()
            entity_mappings = parse_llm_output(generated_text)
            return entity_mappings
        elif provider.lower() == 'ollama':
            # For Ollama Client
            response = client.generate(prompt)
            generated_text = response.strip()
            entity_mappings = parse_llm_output(generated_text)
            return entity_mappings
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        logging.error(f"Error generating entity mappings with {provider}: {e}")
        raise Exception(f"LLM generation failed: {e}")


def integrate_llm_in_entity_matching(similarity_df, client, provider: str, model_name: str):
    """
    Use LLM to enhance entity matching, especially for ambiguous cases.

    Args:
        similarity_df (DataFrame): DataFrame containing entities and similarity scores.
        client (object): The LLM client instance.
        provider (str): The name of the LLM provider.
        model_name (str): The LLM model to use.

    Returns:
        DataFrame: An updated DataFrame with improved entity matching.

    Side Effects:
        May involve additional API calls to the LLM provider.
    """
    import pandas as pd
    import streamlit as st

    st.write("Enhancing entity matching using LLM...")

    # Filter ambiguous cases
    ambiguous_cases = similarity_df[
        (similarity_df['SimilarityScore'] < 0.9) &
        (similarity_df['SimilarityScore'] > 0.5)
    ]

    if ambiguous_cases.empty:
        st.write("No ambiguous cases to process with LLM.")
        return similarity_df

    enhanced_mappings = {}

    for idx, row in ambiguous_cases.iterrows():
        entity_a = row['EntityA']
        entity_b = row['EntityB']
        prompt = f"Do the following entities refer to the same real-world entity? Provide 'Yes' or 'No' along with a brief explanation.\nEntity 1: {entity_a}\nEntity 2: {entity_b}\nAnswer:"
        st.write(f"Processing entities: '{entity_a}' and '{entity_b}' using LLM...")
        try:
            result = generate_entity_mappings_with_llm(prompt, client, provider, model_name)
            # Assuming result is a dict with a 'decision' key
            decision = result.get('decision', '').lower()
            if 'yes' in decision:
                similarity_df.at[idx, 'LLM_Match'] = True
            else:
                similarity_df.at[idx, 'LLM_Match'] = False
        except Exception as e:
            st.error(f"Failed to process entities with LLM: {e}")
            similarity_df.at[idx, 'LLM_Match'] = None  # Indicate failure to decide

    st.write("LLM-enhanced entity matching completed.")
    return similarity_df


def parse_llm_output(output_text: str) -> Dict[str, Any]:
    """
    Parse the output text from the LLM into a structured dictionary.

    Args:
        output_text (str): The raw text output from the LLM.

    Returns:
        dict: A dictionary containing parsed results.

    Implementation Notes:
        The parsing logic will depend on the expected format of the LLM output.
        For example, if the LLM outputs JSON-formatted text, we can use json.loads().
        If the output is plain text, we may need to use regular expressions or other parsing techniques.
    """
    import json
    try:
        # Try parsing as JSON
        parsed_output = json.loads(output_text)
        return parsed_output
    except json.JSONDecodeError:
        # Fallback parsing for plain text
        lines = output_text.strip().split('\n')
        decision = ' '.join(lines).lower()
        return {'decision': decision}