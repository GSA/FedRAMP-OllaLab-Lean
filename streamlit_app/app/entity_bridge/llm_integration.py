# streamlit_app/app/entity_bridge/llm_integration.py

"""
LLM Integration Module

This module provides functions to integrate with various Large Language Models (LLMs)
such as OpenAI, Ollama, Anthropic, Google Vertex AI, and AWS Bedrock.
"""

import os
import logging
from typing import Any, Dict
import json
import re

# Import necessary clients or SDKs for each provider
# Note: Users must install the required SDKs for each provider they intend to use.

# Ollama
try:
    import ollama
    from ollama import Client as OllamaClient
    import requests
except ImportError:
    OllamaClient = None

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
    from google.oauth2 import service_account
    from vertexai.preview.language_models import ChatModel
except ImportError:
    aiplatform = None
    service_account = None
    ChatModel = NotImplementedError

# AWS Bedrock (Note: AWS SDK supports Bedrock in later versions)
try:
    import boto3
except ImportError:
    boto3 = None

def setup_llm_client(provider: str, selected_model: str = None, **credentials) -> Any:
    """
    Set up the LLM client based on the selected provider and credentials.

    Args:
        provider (str): The name of the LLM provider ('ollama', 'openai', 'anthropic', 'vertexai', 'bedrock').
        selected_model (str): The name of the LLM model to use.
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
        openai_client = OpenAI(api_key=api_key)
        return openai_client
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
        project_id = credentials.get('project_id')
        location = credentials.get('location','us-central')
        credentials_info = credentials.get('credentials_info')
        if not project_id:
            raise ValueError("Project ID is required for Google Vertex")
        if credentials_info:
            credentials_obj = service_account.Credentials.from_service_account_info(credentials_info)
        else:
            credentials_obj = None #assuming default credential
        aiplatform.init(project=project_id, location=location, credentials=credentials_obj)
        return aiplatform
    elif provider.lower() == 'bedrock':
        if boto3 is None:
            raise ImportError("Boto3 library is not installed. Please install it with 'pip install boto3'.")
        # AWS credentials are typically handled via environment variables or configuration files.
        aws_access_key_id = credentials.get('aws_access_key_id')
        aws_secret_access_key = credentials.get('aws_secret_access_key')
        aws_session_token = credentials.get('aws_session_token')
        region_name = credentials.get('region_name', 'us-east-1')
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError("AWS credentials are required for Amazon Bedrock.")
        session = boto3.Session(
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key,
            aws_session_token = aws_session_token,
            region_name = region_name
        )
        client = boto3.client('bedrock-runtime') #or "bedrock"
        return client
    elif provider.lower() == 'ollama':
        if OllamaClient is None:
            raise ImportError("Ollama client library is not installed. Please install it using 'pip install -U ollama.'")
        base_url = credentials.get('base_url', 'http://localhost:11434')
        client = OllamaClient(host=base_url)
        return client
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def generate_entity_mappings_with_llm(prompt: str, client: Any, provider: str, model_name: str, **kwargs) -> Dict[str, Any]:
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
        generated_text = ""
        if provider.lower() == 'openai':
            # For OpenAI, using ChatCompletion API
            response = client.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
                #n=1,
                #stop=None,
                temperature=0.1,
            )
            generated_text = response.choices[0].message['content'].strip()
        elif provider.lower() == 'anthropic':
            # For Anthropic's Claude API
            response = client.completion(
                prompt=prompt,
                model=model_name,
                max_tokens_to_sample=500,
                stop_sequences=[],
                temperature=0.1,
            )
            generated_text = response.get('completion', '').strip()
        elif provider.lower() == 'vertexai':
            # For Google Vertex AI
            # Assuming use of Text Generation models
            model = client.TextGenerationModel.from_pretrained(model_name)
            response = model.predict(prompt)
            generated_text = response.text.strip()
        elif provider.lower() == 'bedrock':
            # For AWS Bedrock
            if "anthropic" in model_name:
                body = json.dumps({
                    "prompt": "\n\nHuman: " + prompt + "\n\nAssistant:",
                    "maxTokens": 500,
                    "temperature": 0.1,
                    "stopSequences": ["\n\nHuman:"]
                })
            elif "ai21" in model_name:
                body = json.dumps({
                    "prompt": prompt,
                    "maxTokens": 500,
                    "temperature": 0.1,
                    "topP":1,
                    "stopSequences": ["<|END"]
                })
            else:
                raise ValueError(f"Unsupported model for Amazon Bedrock: {model_name}")
            response = client.invoke_model(
                modelId=model_name,
                accept='application/json',
                contentType='application/json',
                body=body
            )
            response_body = response['body'].read().decode('utf-8')
            response_json = json.loads(response_body)
            if "result" in response_json:
                generated_text = response_json['result']
            elif "completion" in response_json:
                generated_text= response_json['completion']
            else:
                raise Exception("Unexpected response format from Amazon Bedrock")

        elif provider.lower() == 'ollama':
            # For Ollama Client
            response = client.chat(
                model=model_name,
                messages=[{'role':'user','content': prompt}]
            )
            generated_text = response["message"]["content"].strip()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if not generated_text:
            raise ValueError("LLLM returned an empty response.")
        
        # Now parse the generated_text to dictionary
        entity_mappings = parse_llm_output(generated_text)
        return entity_mappings
    
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
        We attempt to extract JSON from the text output.
    """
    import json
    import re
    try:
        # Attempt to extract JSON from the output_text
        json_pattern = r'\{(?:[^{}]|(?R))*\}'
        matches = re.findall(json_pattern, output_text, flags=re.DOTALL)
        if matches:
            # Attempt to parse each match until successful
            for json_str in matches:
                try:
                    parsed_output = json.loads(json_str)
                    return parsed_output
                except json.JSONDecodeError:
                    continue
            raise ValueError("Failed to parse JSON content from LLM output")
        else:
            raise ValueError("No JSON content found in LLM output")
    except Exception as e:
        raise ValueError(f"Error parsing LLM output: {e}")

def infer_true_parents(parent_names_list, parent_entity_type, client, provider, model_name):
    """
    Use the LLM to infer true parents of related entities.

    Args:
        parent_names_list (list): List of unique parent names.
        parent_entity_type (str): Type of parent entity.
        client (object): The LLM client instance.
        provider (str): The name of the LLM provider.
        model_name (str): The LLM model to use.

    Returns:
        dict: A dictionary containing groups of parent names and their inferred true parent.
    """
    # Construct the prompt
    prompt_template = (
        "Given the following list of entities: {parent_names_list},\n"
        "Based on your knowledge of real-world relationships, determine if it is plausible to group some of these entities that share a common parent entity of type {parent_entity_type}.\n"
        "For each identified group, identify the name of the potential parent entity that could encompass all of the group's members.\n"
        "Respond only with valid JSON. Do not write an introduction or summary.\n"
    )

    # Replace placeholders
    parent_names_str = ', '.join([f'"{name}"' for name in parent_names_list])
    prompt = prompt_template.format(
        parent_names_list=parent_names_str,
        parent_entity_type=parent_entity_type
    )

    # Call the LLM
    result = generate_entity_mappings_with_llm(prompt, client, provider, model_name)

    # Return the result
    return result