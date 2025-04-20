#!/bin/sh
echo "Starting Ollama service..."
ollama serve &
echo "Waiting for Ollama service to initialize (10 seconds)..."
sleep 10
MODELS=${OLLAMA_MODELS:-"llama3:8b"}
echo "==================================="
echo "Starting model installation process"
echo "Models to be installed: $MODELS"
echo "==================================="
for MODEL in $(echo $MODELS | tr ',' ' '); do
  echo "==================================="
  echo "Starting installation of model: $MODEL"
  echo "This may take several minutes..."
  echo "==================================="
  ollama pull $MODEL
  if [ $? -eq 0 ]; then
    echo "✓ Successfully installed model: $MODEL"
  else
    echo "✗ Failed to install model: $MODEL"
  fi
  echo "==================================="
done
echo "All model installations completed"
echo "Ollama service is running..."
wait