#!/bin/bash

# Change working directory to your Rasa project
cd /app/rasa_project

echo "Starting action server on port 5055..."
rasa run actions --port 5055 --actions actions &

echo "Starting Rasa server on port ${PORT:-5005}..."
rasa run \
  --enable-api \
  --port ${PORT:-5005} \
  --cors "*" \
  --endpoints endpoints.yml \
  --model models
