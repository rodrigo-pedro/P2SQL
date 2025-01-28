FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r llm_guard/requirements.txt

WORKDIR /app/llm_guard

CMD ["python3", "llm_guard_eval.py"]
