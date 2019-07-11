FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt src/ ./
COPY bin/ /usr/bin/

RUN apk --update add git less openssh && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/* && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install awscli
