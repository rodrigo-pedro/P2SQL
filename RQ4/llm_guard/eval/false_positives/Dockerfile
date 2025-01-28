FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r deberta_row/requirements.txt

WORKDIR /app/deberta_row

CMD ["python3", "llm_guard_eval.py"]
