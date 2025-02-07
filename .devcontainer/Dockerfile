FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

COPY requirements.lock .
RUN pip install -r requirements.lock && \
    apt-get update && \
    apt-get install -y fonts-noto-cjk fontconfig && \
    fc-cache -fv && \
    apt-get clean && \
    apt-get install -y nodejs npm && \