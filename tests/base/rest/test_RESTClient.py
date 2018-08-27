from unittest import TestCase

from cryptoverse.base.rest import RESTClient

rc = RESTClient('httpbin.org')


class TestRESTClient(TestCase):
    def test___init__(self):
        self.assertEqual(rc.host, 'httpbin.org')

    def test_nonce(self):
        response = rc.nonce()
        self.assertIsInstance(response, str)
