#!/usr/bin/env python
import json

import pika

from constants import *

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare an exchange (topic exchange in this case)
channel.exchange_declare(exchange=FromCentralServiceToMicroService, exchange_type='topic')

# channel.queue_declare(queue='hello')
order = {
    HashKey: "124",
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
    HashKey: "124",
    "order_id": 1,
    "status": "Delivered"
}
get_orders = {
    HashKey: "124"
}

# Convert the dictionary to a JSON string
json_data = json.dumps(order)
print(json_data)

# channel.basic_publish(exchange=FromAppToKitchen, routing_key=AddOrder, body=json_data)
# json_data = json.dumps(status)
# print(json_data)
# channel.basic_publish(exchange=FromAppToKitchen, routing_key=ChangeStatus, body=json_data)
json_data = json.dumps(get_orders)
channel.basic_publish(exchange=FromCentralServiceToMicroService, routing_key=GetOrders, body=json_data)
print(" [x] Sent 'Hello World!'")
connection.close()
