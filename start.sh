#!/bin/bash

cd /app/rasa_project || exit

echo "Starting Rasa action server on port 5055..."
rasa run actions --port 5055 &

echo "========== STARTING RASA SERVER =========="
exec rasa run \
  --enable-api \
  --port 5005 \
  --cors "*" \
  --endpoints endpoints.yml \
  --model models
