FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends --yes build-essential

RUN python3.9 -m pip install -r requirements.txt

COPY . .

CMD python3.9 chatbot.py