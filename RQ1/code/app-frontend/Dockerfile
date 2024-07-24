FROM python:3-slim

RUN pip install gradio

COPY app_frontend.py ./

ENTRYPOINT [ "python", "app_frontend.py" ]
