from confluent_kafka import Producer


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
    topic = "my-topic"  # Replace with your Kafka topic
    message = 'Hello, Kafka!'

    produce_message(bootstrap_servers, topic, message)
