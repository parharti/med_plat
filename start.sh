#!/bin/bash
set -e

# Start Rasa action server in background
rasa run actions &

# Start main Rasa server in foreground
rasa run \
  --enable-api \
  --model /app/rasa_project/models \
  --endpoints /app/rasa_project/endpoints.yml \
  --cors "*" \
  --debug

