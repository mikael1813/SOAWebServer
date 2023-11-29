import json

from confluent_kafka import Producer

from App.constants import *


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_message(bootstrap_servers, topic, message):
    producer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'python-producer'
    }

    producer = Producer(producer_conf)

    # Produce a message to the specified topic
    producer.produce(topic, value=message, callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery reports to be received
    producer.flush()


if __name__ == '__main__':
    bootstrap_servers = 'localhost:9092'  # Replace with your Kafka bootstrap servers
    topic = FromCentralServiceToMicroService  # Replace with your Kafka topic
    message = {
        HashKey: "124",
        AddFood:
            [
                {
                    "food": "mar",
                    "price": 500,
                    "available": True
                }
            ]
    }
    # message = {
    #     HashKey: "124",
    #     RemoveFood:
    #         [
    #             1
    #         ]
    # }
    message = json.dumps(message)

    produce_message(bootstrap_servers, topic, message)

    # message = {
    #     HashKey: "124",
    #     UpdateFood:
    #         [
    #             {
    #                 "id": 2,
    #                 "food": "para",
    #                 "price": 200,
    #                 "available": False
    #             }
    #         ]
    # }

    message = {
        HashKey: "124",
        GetAllFoods: ""
    }

    message = json.dumps(message)

    produce_message(bootstrap_servers, topic, message)
