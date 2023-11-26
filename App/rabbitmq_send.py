#!/usr/bin/env python
import json

import pika

from App.constants import *

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare an exchange (topic exchange in this case)
channel.exchange_declare(exchange='example_exchange', exchange_type='topic')

# channel.queue_declare(queue='hello')
order = {
    "user_id": 1,
    "foods": [
        {
            "food_id": 1,
            "quantity": 2
        },
        {
            "food_id": 2,
            "quantity": 1
        }
    ]
}
status = {
    "order_id": 1,
    "status": "Delivered"
}

# Convert the dictionary to a JSON string
json_data = json.dumps(order)
print(json_data)

channel.basic_publish(exchange='example_exchange', routing_key=AddOrder, body=json_data)
json_data = json.dumps(status)
print(json_data)
channel.basic_publish(exchange='example_exchange', routing_key=ChangeStatus, body=json_data)
print(" [x] Sent 'Hello World!'")
connection.close()
