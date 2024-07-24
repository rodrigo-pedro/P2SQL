FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
