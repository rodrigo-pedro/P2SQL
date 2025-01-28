FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["python3", "server.py"]
