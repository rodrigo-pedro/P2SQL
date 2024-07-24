FROM python:3.11-buster

WORKDIR /app

ADD requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

ADD deployment deployment

RUN cd deployment && \
    pip3 install .

#ADD customer.csv app.py ./

ADD job-postings.csv app.py ./

CMD ["python3", "app.py"]
