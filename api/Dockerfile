# Use alpine image for smaller size and improved container security 
FROM python:3.7-alpine3.13

WORKDIR /usr/src/app

COPY ./requirements.txt .

# Disactivate cache for reproducible builds
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY config.py .

EXPOSE 5000
ENV FLASK_APP=api.py

CMD ["flask", "run"]