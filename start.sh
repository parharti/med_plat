#!/bin/bash
set -e

echo "🟢 Starting Rasa action server..."
rasa run actions &

echo "🟢 Starting main Rasa server..."
rasa run \
  --enable-api \
  --model /app/rasa_project/models \
  --endpoints /app/rasa_project/endpoints.yml \
  --cors "*" \
  --debug

wait

