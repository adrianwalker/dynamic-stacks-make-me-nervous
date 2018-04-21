import json
import uuid

import pika

import datastore


class Consumer(object):

    def __init__(self, host='localhost', queue='person', bucket='person'):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=queue)
        self.dataStore = datastore.DataStore(bucket)

    def on_request(self, channel, method, properties, body):

        request = json.loads(body)
        errors = self.validate(request)
        if errors:
            response = {
                'status': 400,
                'error': ', '.join(errors)
            }
        else:
            response = self.save(request)

        self.channel.basic_publish(exchange='',
                                   routing_key=properties.reply_to,
                                   properties=pika.BasicProperties(
                                       correlation_id=properties.correlation_id),
                                   body=json.dumps(response))
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        self.channel.start_consuming()

    def validate(self, request):

        errors = []

        if 'first_name' not in request or not request['first_name']:
            errors.append('Invalid or missing first name')

        if 'last_name' not in request or not request['last_name']:
            errors.append('Invalid or missing last name')

        return errors

    def save(self, request):

        id = str(uuid.uuid4())
        try:
            self.dataStore.save(id, request)
            response = {
                'id': id,
                'status': 201,
            }
        except Exception as e:
            response = {
                'status': 500,
                'error': str(e)
            }

        return response


def main():
    consumer = Consumer()
    consumer.consume()


if __name__ == '__main__':
    main()
