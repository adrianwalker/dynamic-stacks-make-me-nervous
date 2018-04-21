import json

import requests


class PersonController(object):
    URL = 'http://%s:%s/person'

    def __init__(self, host='localhost', port=8888):
        self.url = self.URL % (host, port)

    def save(self, person):
        response = requests.post(self.url, data=json.dumps(person, default=lambda x: x.__dict__))
        if response.status_code != 201:
            raise Exception(response.status_code, response.json()['error'])

        return response.json()['id']


class Person(object):

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.age = None
        self.email = None


def main():
    person = Person()
    person.first_name = 'Adrian'
    person.last_name = 'Walker'
    person.age = 36
    person.email = 'adrian.walker@bcs.org'

    controller = PersonController()
    id = controller.save(person)
    print id


if __name__ == '__main__':
    main()
