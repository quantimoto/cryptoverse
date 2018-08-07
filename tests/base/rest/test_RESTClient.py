from unittest import TestCase

from cryptoverse.base.rest import RESTClient

rc = RESTClient('httpbin.org')


class TestRESTClient(TestCase):
    def test___init__(self):
        self.assertEqual(rc.host, 'httpbin.org')

    def test__create_url(self):
        response = rc._create_url(path='{command}', path_params={'command': 'get'})
        self.assertEqual(response, 'https://httpbin.org/get')

    def test_nonce(self):
        response = rc.nonce()
        self.assertIsInstance(response, str)
