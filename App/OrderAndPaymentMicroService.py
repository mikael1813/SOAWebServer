import json
import os
import sys

import pika

from App.Database import RestaurantDB
from constants import *


class OrderAndPaymentMicroService:

    def __init__(self):
        self.db = RestaurantDB()

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Declare an exchange and queues
        channel.exchange_declare(exchange='example_exchange', exchange_type='topic')

        channel.queue_declare(queue=FromAppToKitchen)
        channel.queue_bind(exchange='example_exchange', queue=FromAppToKitchen, routing_key=AddOrder)
        channel.queue_bind(exchange='example_exchange', queue=FromAppToKitchen, routing_key=ChangeStatus)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(data)
            if method.routing_key == AddOrder:
                self.add_order(data["user_id"], data["foods"])
            elif method.routing_key == ChangeStatus:
                self.change_status(data["order_id"], data["status"])

        channel.basic_consume(queue=FromAppToKitchen, on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def add_order(self, user_id: int, foods: list):
        order_id = self.db.add_order(user_id, "Sent")

        for food in foods:
            food_id = food["food_id"]
            quantity = food["quantity"]
            self.db.add_order_details(order_id, food_id, quantity)

        print(f"Succesfully added order {order_id}")

    def change_status(self, order_id: int, status: str):
        self.db.update_order_stats(order_id, status)

        print(f"Succesfully changed status for order with id={order_id} to {status}")


o = OrderAndPaymentMicroService()
