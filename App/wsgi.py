import json
import socket
from threading import Thread

import pika
from confluent_kafka import Consumer, KafkaError
from flask import Flask

from constants import *

app = Flask(__name__)


@app.route("/")
def home():
    return f"Container ID: {socket.gethostname()}"


class MainService:
    def __init__(self):
        self.__init_rabbitmq()
        self.__init_kafka()
        self.menu_messages = []
        self.order_messages = []

    def __init_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Declare an exchange and queues
        channel.exchange_declare(exchange=FromMicroServiceToCentralService, exchange_type='topic')

        channel.queue_declare(queue=FromMicroServiceToCentralService)
        channel.queue_bind(exchange=FromMicroServiceToCentralService, queue=FromMicroServiceToCentralService,
                           routing_key=GetOrders)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(data)
            if method.routing_key == GetOrders:
                print("ouiiii")
                print(body)

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
                            first_key = next(iter(data))
                            if first_key == GetFood:
                                print(data)
                        except json.decoder.JSONDecodeError:
                            print("not json")

            except KeyboardInterrupt:
                pass
            finally:
                # Close down consumer to commit final offsets.
                consumer_0.close()

        self.kafka_thread = Thread(target=start_consuming, args=(consumer,))
        self.kafka_thread.start()


if __name__ == "__main__":
    MainService()
    # app.run(host="0.0.0.0", debug=True)
