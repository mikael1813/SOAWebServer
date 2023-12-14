FROM python:3.9-slim

WORKDIR /UserMicroService

COPY . .

RUN pip install -r requirments.txt

CMD gunicorn --bind 0.0.0.0:8001 UserMicroService:user_app