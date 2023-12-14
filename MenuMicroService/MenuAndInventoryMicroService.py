import json

from confluent_kafka import Consumer, KafkaError, Producer
from constants import *

from Database import RestaurantDB


class MenuAndInventoryMicroService:
    def __init__(self):
        self.db = RestaurantDB()

        self.init_kafka_consumer()

    def init_kafka_consumer(self):
        bootstrap_servers = 'localhost:9092'  # Replace with your Kafka bootstrap servers
        group_id = FromCentralServiceToMicroService  # Replace with your consumer group ID
        topic = FromCentralServiceToMicroService  # Replace with your Kafka topic

        consumer_conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'  # Start consuming from the beginning of the topic
        }

        consumer = Consumer(consumer_conf)
        consumer.subscribe([topic])

        try:
            while True:
                msg = consumer.poll(0.1)  # Poll for messages, with a timeout of 1 second

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
                        for key in data:
                            if key != HashKey:
                                first_key = key
                                break
                        hash_key = data[HashKey]
                        return_message = {
                            HashKey: hash_key
                        }
                        if first_key == AddFood:
                            self.add_food(data[AddFood])
                        elif first_key == RemoveFood:
                            self.remove_food(data[RemoveFood])
                        elif first_key == UpdateFood:
                            self.update_food(data[UpdateFood])
                        # elif first_key == GetAllFoods:
                        foods = self.get_all_foods()
                        return_message[Body] = foods
                        return_message = json.dumps(return_message)
                        self.send_message_to_central_service(return_message)

                    except json.decoder.JSONDecodeError:
                        print("not json")

        except KeyboardInterrupt:
            pass
        finally:
            # Close down consumer to commit final offsets.
            consumer.close()

    def add_food(self, foods):
        for food in foods:
            self.db.add_menu(food["food"], food["price"], food["available"])

    def update_food(self, foods):
        for food in foods:
            self.db.update_menu(food["id"], food["food"], food["price"], food["available"])

    def remove_food(self, ids):
        for menu_id in ids:
            self.db.remove_menu(menu_id)

    def get_all_foods(self) -> str:
        return self.db.get_all_foods()

    def delivery_report(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def send_message_to_central_service(self, message: str) -> None:
        bootstrap_servers = 'localhost:9092'  # Replace with your Kafka bootstrap servers
        topic = FromMicroServiceToCentralService  # Replace with your Kafka topic

        producer_conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'python-producer'
        }

        producer = Producer(producer_conf)

        # Produce a message to the specified topic
        producer.produce(topic, value=message, callback=self.delivery_report)

        # Wait for any outstanding messages to be delivered and delivery reports to be received
        producer.flush()


m = MenuAndInventoryMicroService()
