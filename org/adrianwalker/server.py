import json
import uuid

import pika
import tornado.web
from tornado.ioloop import IOLoop


class Publisher(object):

    def __init__(self, host='localhost', queue='person'):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)
        self.response = None
        self.correlation_id = None
        self.queue = queue

    def on_response(self, channel, method, properties, body):
        if self.correlation_id == properties.correlation_id:
            self.response = body

    def publish(self, data):

        self.correlation_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.correlation_id,
                                   ),
                                   body=data)
        while self.response is None:
            self.connection.process_data_events()

        return self.response


class Handler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Handler, self).__init__(application, request, **kwargs)
        self.publisher = Publisher()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def prepare(self):
        try:
            self.request.arguments.update(json.loads(self.request.body))
        except ValueError:
            self.send_error(400, message='Error parsing JSON')

    def post(self):
        response = json.loads(self.publisher.publish(self.request.body.decode('utf-8')))
        self.set_status(response['status'])
        self.write(json.dumps(response))
        self.flush()


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/person/?', Handler)
        ]
        tornado.web.Application.__init__(self, handlers)

    def listen(self, address='localhost', port=8888, **kwargs):
        super(Application, self).listen(port, address, **kwargs)


def main():
    application = Application()
    application.listen()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
