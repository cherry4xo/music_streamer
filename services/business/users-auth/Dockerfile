FROM python:3.13-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/home/code/ PYTHONHASHSEED=0

COPY ./requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r requirements.txt

WORKDIR /usr/src/users

COPY ./app/ app/
COPY ./main.py ./