FROM python:3-slim-bullseye

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST 0.0.0.0

RUN apt-get update && apt-get install -y python3-pip &&\
    pip install fastapi uvicorn openai psycopg2-binary langchain==0.0.189

COPY app_backend.py ./


# Run the server
ENTRYPOINT ["python", "app_backend.py"]
