from confluent_kafka import Consumer, KafkaError


def consume_messages(bootstrap_servers, group_id, topic):
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'  # Start consuming from the beginning of the topic
    }

    consumer = Consumer(consumer_conf)
    print(consumer.list_topics().topics)
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for messages, with a timeout of 1 second

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

    except KeyboardInterrupt:
        pass
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


if __name__ == '__main__':
    bootstrap_servers = 'localhost:9092'  # Replace with your Kafka bootstrap servers
    group_id = 'group1'  # Replace with your consumer group ID
    topic = 'menu'  # Replace with your Kafka topic

    consume_messages(bootstrap_servers, group_id, topic)
