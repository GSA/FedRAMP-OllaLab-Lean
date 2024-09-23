#!/bin/bash

# Start Ollama server in the background
ollama serve

# Wait for the server to be ready
until curl -s http://localhost:8000; do
  echo "Waiting for Ollama server..."
  sleep 5
done

# Load the llama3.1:8b model
ollama pull llama3.1:8b

# Keep the container running
tail -f /dev/null
