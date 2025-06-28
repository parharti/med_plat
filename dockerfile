# Use official Rasa image
FROM rasa/rasa:3.6.20-full

# Set working directory
WORKDIR /app

# Switch to root for installation
USER root
# Install supervisor
RUN apt-get update && apt-get install -y supervisor


# Copy requirements early and install
COPY rasa_project/requirements.txt ./requirements.txt
RUN pip install --break-system-packages -r requirements.txt

# Copy your code
COPY rasa_project/ ./rasa_project/
COPY middleware/server.py ./server.py
COPY app.py ./app.py
COPY supervisord.conf /etc/supervisord.conf  

# Train Rasa model
WORKDIR /app/rasa_project
RUN rasa train

# Go back to app root
WORKDIR /app

# ✅ Clear Rasa image's default ENTRYPOINT so supervisord works
ENTRYPOINT []

# ✅ Optional: switch to non-root user for runtime
USER 1001

# Expose necessary ports
EXPOSE 5005
EXPOSE 8080
EXPOSE 3000

# Start supervisord to manage Rasa + Flask
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
