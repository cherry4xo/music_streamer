FROM python:3.13-slim-bullseye

ARG SERVICE_PATH

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/home/code/ PYTHONHASHSEED=0
ENV API_HOST=0.0.0.0
ENV API_PORT=8080

COPY ${SERVICE_PATH}/requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r requirements.txt

WORKDIR /usr/src/users

COPY ${SERVICE_PATH}/app/ app/
COPY ${SERVICE_PATH}/main.py ./
COPY ${SERVICE_PATH}/migrations/ ./migrations/

CMD python3 -u -m uvicorn main:app --host "${API_HOST}" --port "${API_PORT}"