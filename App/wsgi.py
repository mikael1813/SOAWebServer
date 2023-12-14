import json
import random
import socket
import time
from threading import Thread, Lock

import jwt
import pika
import requests

from confluent_kafka import Consumer, KafkaError
from confluent_kafka import Producer
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from pika.exceptions import AMQPConnectionError
from flask_socketio import SocketIO

from constants import *


class MessageStorage:
    def __init__(self):
        self.menu_messages = []
        self.order_messages = []


storage = MessageStorage()
y = storage.menu_messages

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
key = 'nostradamus4621'

auth = HTTPBasicAuth()

waiting_time_in_seconds = 30
lock = Lock()


# New function to send a message from the server to all clients
def send_message_from_server(message):
    socketio.emit('message_from_server', message)


#
class MainService:
    menu_messages = []
    order_messages = []
    channel = None
    connection = None

    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        while True:
            time.sleep(1)
            try:
                # self.connection = pika.BlockingConnection(
                #     pika.ConnectionParameters(host='rabbitmq'))
                MainService.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                break
            except AMQPConnectionError:
                pass
        MainService.channel = self.connection.channel()

        # Declare an exchange (topic exchange in this case)
        MainService.channel.exchange_declare(exchange=FromCentralServiceToMicroService, exchange_type='topic')
        self.__init_rabbitmq()
        self.__init_kafka()

    def __init_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Declare an exchange and queues
        channel.exchange_declare(exchange=FromMicroServiceToCentralService, exchange_type='topic')

        channel.queue_declare(queue=FromMicroServiceToCentralService)
        channel.queue_bind(exchange=FromMicroServiceToCentralService, queue=FromMicroServiceToCentralService,
                           routing_key=GetOrders)

        def callback(ch, method, properties, body):
            # lock.acquire()
            data = json.loads(body)
            if method.routing_key == GetOrders:
                print("received orders " + json.dumps(data))
                # socketio.emit('message_from_server', "hahaahahahahaha")
                socketio.emit('get_orders', data)
                # send_message_from_server(data)
                # send_message_from_server(json.dumps(data))
                # storage.order_messages.append(data)
            # lock.release()

        channel.basic_consume(queue=FromMicroServiceToCentralService, on_message_callback=callback, auto_ack=True)

        def start_consuming(ch):
            print(' [*] Waiting for rabbitmq messages. To exit press CTRL+C')
            ch.start_consuming()

        self.rabbit_mq_thread = Thread(target=start_consuming, args=(channel,))
        self.rabbit_mq_thread.start()

    def __init_kafka(self):
        bootstrap_servers = 'localhost:9092'  # Replace with your Kafka bootstrap servers
        group_id = FromMicroServiceToCentralService  # Replace with your consumer group ID
        topic = FromMicroServiceToCentralService  # Replace with your Kafka topic

        consumer_conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'  # Start consuming from the beginning of the topic
        }

        consumer = Consumer(consumer_conf)
        consumer.subscribe([topic])

        def start_consuming(consumer_0):
            try:
                while True:
                    msg = consumer_0.poll(0.1)  # Poll for messages, with a timeout of 1 second

                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            # End of partition event
                            print("Reached end of partition, consumer will exit")
                        else:
                            print("Error: {}".format(msg.error()))
                    else:
                        # Print the received message value
                        print('Received message: {}'.format(msg.value().decode('utf-8')))
                        try:
                            data = json.loads(msg.value())
                            lock.acquire()
                            print("received foods")
                            socketio.emit('get_food', data)
                            # send_message_from_server(json.dumps(data))
                            # storage.menu_messages.append(data)
                            lock.release()
                            # first_key = data[Body]
                            # if first_key == GetFood:
                            #     self.menu_messages.append()
                            #     print(data)
                        except json.decoder.JSONDecodeError:
                            print("not json")

            except KeyboardInterrupt:
                pass
            finally:
                # Close down consumer to commit final offsets.
                consumer_0.close()

        self.kafka_thread = Thread(target=start_consuming, args=(consumer,))
        self.kafka_thread.start()

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    @staticmethod
    def produce_message(message):
        producer_conf = {
            'bootstrap.servers': 'localhost:9092',
            'client.id': 'python-producer'
        }
        message = json.dumps(message)
        producer = Producer(producer_conf)

        # Produce a message to the specified topic
        producer.produce(FromCentralServiceToMicroService, value=message, callback=MainService.delivery_report)

        # Wait for any outstanding messages to be delivered and delivery reports to be received
        producer.flush()

    @staticmethod
    def send_message_to_orders_micro_service(msg, routing_key):

        json_data = json.dumps(msg)

        MainService.channel.basic_publish(exchange=FromCentralServiceToMicroService, routing_key=routing_key,
                                          body=json_data)

    @staticmethod
    def generate_random_hash():
        return random.getrandbits(128)

    @staticmethod
    @app.route("/")
    def home():
        return f"Container ID: {socket.gethostname()}"

    @staticmethod
    def generate_auth_token(user_mail, expires_in=600):
        return jwt.encode({'mail': user_mail, 'exp': time.time() + expires_in},
                          key=key, algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, key=key,
                              algorithms=['HS256'])
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    @app.route('/user/login', methods=["POST"])
    @auth.login_required
    def login():
        mail_or_token = request.json['mail_or_token']

        api_url = 'http://localhost:8001/user/id'
        user = {'mail': mail_or_token}
        r = requests.get(url=api_url, json=user)

        user_id = r.text

        token = MainService.generate_auth_token(mail_or_token, 300)
        return jsonify({'token': token, 'duration': 300, 'user_id': user_id})

    @staticmethod
    @app.route('/user', methods=["POST"])
    def add_user():
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        phone_number = request.json['phone_number']
        mail = request.json['mail']
        password = request.json['password']

        api_url = 'http://localhost:8001/user'
        create_row_data = {'firstname': firstname, 'lastname': lastname, 'phone_number': phone_number, 'mail': mail,
                           'password': password}
        print(create_row_data)
        r = requests.post(url=api_url, json=create_row_data)
        print(r.status_code, r.reason, r.text)
        return Response(
            r.text,
            status=r.status_code,
        )

    @staticmethod
    @app.route('/menu', methods=["POST"])
    @auth.login_required
    def add_food():
        food = request.json['food']
        price = request.json['price']
        available = request.json['available']

        message = {
            HashKey: MainService.generate_random_hash(),
            AddFood:
                [
                    {
                        "food": food,
                        "price": price,
                        "available": available
                    }
                ]
        }
        MainService.produce_message(message)

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @app.route('/menu', methods=["PUT"])
    @auth.login_required
    def update_food():
        food_id = request.json['id']
        food = request.json['food']
        price = request.json['price']
        available = request.json['available']

        message = {
            HashKey: MainService.generate_random_hash(),
            UpdateFood:
                [
                    {
                        "id": food_id,
                        "food": food,
                        "price": price,
                        "available": available
                    }
                ]
        }
        MainService.produce_message(message)

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @app.route('/menu', methods=["DELETE"])
    @auth.login_required
    def delete_food():
        food_id = request.json['id']

        message = {
            HashKey: MainService.generate_random_hash(),
            RemoveFood:
                [
                    food_id
                ]
        }
        MainService.produce_message(message)

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @app.route('/menu', methods=["GET"])
    # @auth.login_required
    def get_all_foods():
        message = {
            HashKey: MainService.generate_random_hash(),
            GetAllFoods: ""
        }
        MainService.produce_message(message)

        # counter = 0
        # while counter < waiting_time_in_seconds:
        #     counter += 1
        #     time.sleep(1)
        #     print(storage.menu_messages)
        #     for el in storage.menu_messages:
        #         if message[HashKey] == el[HashKey]:
        #             return Response(
        #                 json.dumps(el[Body])
        #             )

        return Response(
            status=200,
        )

    @staticmethod
    @app.route('/orders', methods=["POST"])
    @auth.login_required
    def add_order():
        msg = request.json['msg']
        msg[HashKey] = MainService.generate_random_hash()

        MainService.send_message_to_orders_micro_service(msg, AddOrder)

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @app.route('/orders', methods=["PUT"])
    @auth.login_required
    def update_order_status():
        order_id = request.json['order_id']
        status = request.json['status']

        msg = {
            HashKey: MainService.generate_random_hash(),
            "order_id": order_id,
            "status": status
        }
        MainService.send_message_to_orders_micro_service(msg, ChangeStatus)

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @app.route('/orders/orders', methods=["POST"])
    @auth.login_required
    def get_all_orders():
        user_id = request.json['user_id']
        get_orders = {
            HashKey: MainService.generate_random_hash(),
            "user_id": user_id
        }
        MainService.send_message_to_orders_micro_service(get_orders, GetOrders)

        # counter = 0
        # while counter < waiting_time_in_seconds:
        #     counter += 1
        #     time.sleep(1)
        #     lock.acquire()
        #     x = storage.order_messages
        #     for el in storage.order_messages:
        #         if get_orders[HashKey] in el[HashKey]:
        #             return Response(
        #                 el[Body]
        #             )
        #     lock.release()

        return Response(
            json.dumps("Ok"),
            status=200,
        )

    @staticmethod
    @auth.verify_password
    def verify_password(mail_or_token, password):
        mail_or_token = request.json['mail_or_token']
        password = request.json['password']
        is_token_ok = MainService.verify_auth_token(mail_or_token)

        if is_token_ok:
            return True

        api_url = 'http://localhost:8001/user'
        user = {'mail': mail_or_token, 'password': password}
        r = requests.get(url=api_url, json=user)
        if r.text == 'success':
            return True

        return False


#


# MainService = MainService('localhost:9092', FromCentralServiceToMicroService)

# class WebSocketHandler(tornado.websocket.WebSocketHandler):
#     def check_origin(self, origin):
#         return True
#
#     def open(self):
#         print("WebSocket connection opened")
#
#     def on_message(self, message):
#         print(f"Received message: {message}")
#         self.write_message(f"Server received: {message}")
#
#     def on_close(self):
#         print("WebSocket connection closed")
#
#     @classmethod
#     def send_to_all_clients(cls, message):
#         for client in cls.connected_clients:
#             client.write_message(message)
#
#
# def make_app():
#     return tornado.web.Application([
#         (r"/websocket", WebSocketHandler),
#     ])
#
#
# def start_web_socket():
#     web_socket = make_app()
#     web_socket.listen(9999)
#     print("WebSocket server is running on ws://localhost:9999/websocket")
#     tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    # MainService()
    # app.run(host="0.0.0.0", debug=True)

    # thread = Thread(target=start_web_socket)
    # thread.start()

    MainService('localhost:9092', FromCentralServiceToMicroService)
    socketio.run(app, port=5080, debug=True, allow_unsafe_werkzeug=True)

    time.sleep(2)

    # app.run(host='localhost', port=5080, debug=True)
    # app.run(host="0.0.0.0", debug=True)
