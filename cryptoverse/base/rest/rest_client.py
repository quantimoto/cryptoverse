import base64
import hashlib
import hmac
import json

import requests
from retry import retry


class RequestObj:
    method = None
    url = None
    params = None
    data = None
    headers = None

    def __init__(self, method=None, url=None, params=None, data=None):
        self.method = method
        self.url = url
        self.params = params
        self.data = data

    def to_dict(self):
        dict_obj = {
            'method': self.method,
            'url': self.url,
            'params': self.params,
            'data': self.data,
        }
        return dict_obj

    @classmethod
    def from_dict(cls, dict_obj):
        obj = cls(
            method=dict_obj['method'],
            url=dict_obj['url'],
            params=dict_obj['params'],
            data=dict_obj['data'],
        )
        return obj

    def __repr__(self):
        s = list()

        kwargs = self.to_dict()
        for kw, arg in kwargs.items():
            if arg is not None:
                s.append('{kw}={arg!r}'.format(kw=kw, arg=arg))
        return '{}({})'.format(self.__class__.__name__, ', '.join(s))

    def set_headers(self, headers):
        self.headers = headers

    def get_headers(self):
        return self.headers

    def get_url(self):
        return self.url

    def get_data(self):
        return self.sanitize_dict(self.data)

    def get_params(self):
        return self.sanitize_dict(self.params)

    @staticmethod
    def sanitize_dict(dict_obj):
        # remove any key/value pairs where the value is None
        return dict((k, v) for k, v in dict_obj.items() if v is not None)


class ResponseObj:
    pass


class RESTClient(object):
    session = None

    url_structure = '{base_url}/{endpoint}'
    base_url = None

    def __init__(self, base_url=None):
        if base_url is not None:
            self.base_url = base_url

    def query(self, endpoint, method='GET', credentials=None, params=None, data=None):
        """
        Send a query to the api host

        :param str endpoint: the endpoint path for the command you want to send to the host.
        :param str method: 'GET' or 'POST'.
        :param dict credentials: a dictionary containing key and secret values.
        :param dict params: Any parameters that should be added to the query url.
        :param dict data: Any form data that should be added to the request.
        :return: ResponseObj containing the response data from the host as well as formatted data.

        :Example:

        >>> r = RESTClient()
        >>> r.base_url = 'https://httpbin.org'
        >>> response = r.query('get' foo='bar')
        >>> response
        <Response [200]>
        >>> response.json()
        {'args': {'foo': 'bar'},
        'headers':
            {'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Host': 'httpbin.org',
            'User-Agent': '...'},
        'origin': '...',
        'url': 'https://httpbin.org/get?foo=bar'}
        """

        if self.base_url is None:
            raise AttributeError("Attribute 'base_url' not set.")
        # params = dict()
        params.update({'base_url': self.base_url})
        # params.update(kwargs)

        # Insert params into url
        params.update({'endpoint': endpoint.format(**params)})
        url = self.url_structure.format(**params)

        # Remove params that were required for insertion into the endpoint or url
        for key in list(params.keys()):
            if '{{{}}}'.format(key) in endpoint:
                del params[key]
            elif '{{{}}}'.format(key) in self.url_structure:
                del params[key]

        request_obj = RequestObj(
            method=method,
            url=url,
            params=params,
            data=data,
        )
        return self.execute(request_obj, credentials)

    @retry(exceptions=requests.exceptions.ConnectionError, tries=3, delay=0, max_delay=None, backoff=1)
    @retry(exceptions=requests.exceptions.ReadTimeout, tries=3, delay=0, max_delay=None, backoff=1)
    def execute(self, request_obj, credentials=None):
        if self.session is None:
            self.session = requests.Session()

        if credentials is not None:
            self.sign(
                request_obj=request_obj,
                credentials=credentials,
            )

        response = self.session.request(
            method=request_obj.method,
            url=request_obj.get_url(),
            params=request_obj.get_params(),
            data=request_obj.get_data(),
            headers=request_obj.get_headers(),
            # timeout=(60, 60)  # Connect, Read,
            allow_redirects=False,
            verify=True,
        )

        return response

    # Authentication methods

    @staticmethod
    def get_nonce():
        return int(time.time() * 100000)

    def sign(self, request_obj, credentials):
        key = credentials['key']
        secret = credentials['secret']

        payload = {
            'request': ('/v{version}/{endpoint}'.format(**request_obj.get_params())),
            'nonce': self.get_nonce(),
        }
        payload.update(request_obj.get_data())
        encoded_payload = base64.b64encode(json.dumps(payload))

        h = hmac.new(secret, encoded_payload, hashlib.sha384)
        signature = h.hexdigest()

        request_obj.headers = {
            'X-BFX-APIKEY': key,
            'X-BFX-PAYLOAD': encoded_payload,
            'X-BFX-SIGNATURE': signature,
        }
