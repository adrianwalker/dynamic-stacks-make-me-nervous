import json
import uuid

import requests


class PersonController(object):
    URL = 'http://%s:%s/person'

    def __init__(self, host='localhost', port=8888):
        self.url = self.URL % (host, port)

    def save(self, person):
        data = person if isinstance(person, dict) else person.__dict__
        response = requests.post(self.url, data=json.dumps(data))
        if response.status_code != 201:
            raise ControllerSaveException(response.status_code, response.json()['error'])

        return uuid.UUID(response.json()['id'])


class ControllerSaveException(Exception):

    def __init__(self, *args, **kwargs):
        super(ControllerSaveException, self).__init__(*args, **kwargs)


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
