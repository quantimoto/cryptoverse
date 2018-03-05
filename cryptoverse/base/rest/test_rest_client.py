from unittest import TestCase

from rest_client import RESTClient


class TestRESTClient(TestCase):

    def test_RESTClient(self):
        class MyClient(RESTClient):
            base_url = 'https://httpbin.org'
            public_endpoint = '/{command}'

            def get(self):


        my_client = MyClient()

        my_client.public_request('get')
