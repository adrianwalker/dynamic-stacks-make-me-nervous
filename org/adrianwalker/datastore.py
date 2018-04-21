import riak


class DataStore(object):

    def __init__(self, bucket, host='localhost', port=10018):
        self.bucket = bucket
        self.client = riak.RiakClient(host=host, http_port=port, protocol='http')

    def save(self, key, data, timeout=5000):
        bucket = self.client.bucket(self.bucket)
        obj = bucket.new(key, data=data)
        obj.store(timeout=timeout)
