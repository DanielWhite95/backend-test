# Use alpine image for smaller size and improved container security 
FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./api.py /app
COPY ./config.py /app

ENV FLASK_APP=api.py

