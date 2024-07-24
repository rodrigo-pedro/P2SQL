#FROM python:3-slim-bullseye

FROM python:3.11.4

RUN apt-get update 

RUN apt-get install -y python3-pip

WORKDIR /app

# Copy ONLY requirements. This layer is cached if this file doesn't change.
COPY requirements.txt . 

# This uses the cached layer if the previous layer was cached aswell.
RUN pip install -r requirements.txt

# Copy the already-cached Python3 requirements.

COPY . .

#RUN apt-get update && apt-get install -y python3-pip && pip install --no-cache-dir -r requirements.txt

# Run the server
# ENTRYPOINT ["streamlit", "run", "Home.py"]

ENTRYPOINT [ "streamlit", "run" ]

CMD ["Home.py", "--browser.gatherUsageStats", "False"]