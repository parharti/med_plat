# Use official Rasa image
FROM rasa/rasa:3.6.20-full

WORKDIR /app

# Install supervisor
USER root
RUN apt-get update && apt-get install -y supervisor

# Install Python requirements
COPY rasa_project/requirements.txt ./requirements.txt
RUN pip install --break-system-packages -r requirements.txt

# Copy Rasa project
COPY rasa_project/ /app/rasa_project/
COPY supervisord.conf /etc/supervisord.conf

# Train Rasa model
WORKDIR /app/rasa_project
RUN rasa train

# Reset working dir & permissions
WORKDIR /app
ENTRYPOINT []
USER 1001

EXPOSE 10000 5055

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
