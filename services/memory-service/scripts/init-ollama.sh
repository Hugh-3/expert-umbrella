#!/bin/bash
set -e

echo "=== Memory Service Setup ==="

# Wait for Ollama to be ready
echo "Waiting for Ollama..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Ollama not ready, waiting..."
    sleep 5
done

echo "Ollama is ready!"

# Pull embedding model
echo "Pulling embedding model: ${EMBEDDING_MODEL:-nomic-embed-text}..."
docker exec memory-ollama ollama pull ${EMBEDDING_MODEL:-nomic-embed-text}

echo "=== Setup Complete ==="
echo "Memory Service: http://localhost:8001"
echo "Qdrant Dashboard: http://localhost:6333/dashboard"
echo "Ollama API: http://localhost:11434"
