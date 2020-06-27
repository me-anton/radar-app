FROM python:3.8-alpine AS django

ENV PYTHONBUFFERED=1
RUN apk add --update --no-cache gcc musl-dev bash postgresql-dev

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /code
WORKDIR /code
COPY ./backend/* /code/