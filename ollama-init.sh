#!/bin/sh
ollama serve &
sleep 10
MODELS=${OLLAMA_MODELS:-"llama3:8b"}
for MODEL in $(echo $MODELS | tr ',' ' '); do
  echo "Pulling model: $MODEL"
  ollama pull $MODEL
done
wait