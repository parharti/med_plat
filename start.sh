#!/bin/bash

echo "Starting action server on port 5055..."
rasa run actions --port 5055 &

echo "Starting Rasa server on port ${PORT:-5005}..."
rasa run \
  --enable-api \
  --port ${PORT:-5005} \
  --cors "*" \
  --endpoints /app/rasa_project/endpoints.yml \
  --model /app/rasa_project/models
