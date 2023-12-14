FROM python:3.9-slim

WORKDIR /OrderMicroService

COPY . .

RUN pip install -r requirments.txt

#CMD ["gunicorn", "--bind", "0.0.0.0:5300", "OrderMicroService.py"]
CMD ["python", "OrderAndPaymentMicroService.py"]