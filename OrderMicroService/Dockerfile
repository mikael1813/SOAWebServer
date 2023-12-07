FROM python:3.9-slim

WORKDIR /OrderMicroService

# Print the current working directory
RUN pwd

COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5300", "OrderMicroService.py"]