FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

COPY requirements.lock .
RUN pip install --upgrade pip && pip install -r requirements.lock