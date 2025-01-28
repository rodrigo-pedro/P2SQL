FROM python:3.10-slim

WORKDIR /app

COPY question_results_thought_deberta_row question_results_thought_deberta_row

RUN pip install -r question_results_thought_deberta_row/requirements.txt

COPY . .

RUN pip install rebuff/rebuff/python-sdk

RUN chmod +x /app/experiment_script.sh

RUN pip install -r plots/requirements.txt

CMD ["bash", "-c", "./experiment_script.sh"]
