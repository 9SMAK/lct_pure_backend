FROM python:3.9-buster

RUN apt-get update

WORKDIR /telegram_bot

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir --disable-pip-version-check -r ./requirements.txt

COPY . .