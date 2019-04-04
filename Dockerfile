FROM python:3.6-alpine
LABEL maintainer="roondar"

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY shutter.py .
COPY requirements.txt .

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
      build-base=0.5-r1 \
    && apk add --no-cache \
      bash \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del build-dependencies \
    && rm -rf /var/cache/apk/*
