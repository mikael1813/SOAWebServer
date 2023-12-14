import json
import time

import pika
from pika.exceptions import AMQPConnectionError

from Database import RestaurantDB
from constants import *


class OrderAndPaymentMicroService:

    def __init__(self):
        self.db = RestaurantDB()

        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        while True:
            time.sleep(1)
            try:
                # connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
                connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
                break
            except AMQPConnectionError:
                pass
        channel = connection.channel()

        # self.db.add_user("x", "x", "x", "x", "x")

        # Declare an exchange and queues
        channel.exchange_declare(exchange=FromCentralServiceToMicroService, exchange_type='topic')

        channel.queue_declare(queue=FromCentralServiceToMicroService)
        channel.queue_bind(exchange=FromCentralServiceToMicroService, queue=FromCentralServiceToMicroService,
                           routing_key=AddOrder)
        channel.queue_bind(exchange=FromCentralServiceToMicroService, queue=FromCentralServiceToMicroService,
                           routing_key=ChangeStatus)
        channel.queue_bind(exchange=FromCentralServiceToMicroService, queue=FromCentralServiceToMicroService,
                           routing_key=GetOrders)

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                hash_key = data[HashKey]
            except json.decoder.JSONDecodeError as je:
                data = None
                hash_key = ''
            print(data)
            return_message = {
                HashKey: hash_key
            }
            if method.routing_key == AddOrder:
                self.add_order(data["user_id"], data["foods"])
            elif method.routing_key == ChangeStatus:
                self.change_status(data["order_id"], data["status"])
            elif method.routing_key == GetOrders:
                return_message[Body] = self.get_all_orders(data["user_id"])
                print(return_message)
                orders = json.dumps(return_message)
                temp_channel = connection.channel()
                temp_channel.exchange_declare(exchange=FromMicroServiceToCentralService, exchange_type='topic')
                temp_channel.basic_publish(exchange=FromMicroServiceToCentralService, routing_key=GetOrders,
                                           body=orders)
                temp_channel.close()

        channel.basic_consume(queue=FromCentralServiceToMicroService, on_message_callback=callback, auto_ack=True)

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
        self.db.update_order_status(order_id, status)

        print(f"Succesfully changed status for order with id={order_id} to {status}")

    def get_all_orders(self, user_id: int):
        orders = self.db.get_all_orders(user_id)
        return orders


o = OrderAndPaymentMicroService()
