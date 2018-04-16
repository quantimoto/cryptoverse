import time

import requests
from retry import retry


class RequestObj:
    """
    The RequestObj stores all parameters required to do an api request. It can be serialized and saved, in order for a
    different host to do the actual request to the provider. The RequestObj can be updated with a new signature, in case
    a previous request failed.

    Credentials are not stored in the RequestObj. When a request has failed, the host that retries it needs to have
    access to the credentials itself.
    """
    method = None
    address = None
    uri = None
    params = None
    data = None
    headers = None

    def __init__(self, method=None, address=None, uri=None, params=None, data=None, headers=None):
        self.set_method(method)
        self.set_address(address)
        self.set_uri(uri)
        self.set_params(params)
        self.set_data(data)
        self.set_headers(headers)

    def to_dict(self):
        dict_obj = {
            'method': self.get_method(),
            'address': self.get_address(),
            'uri': self.get_uri(),
            'params': self.get_params(),
            'data': self.get_data(),
            'header': self.get_headers(),
        }
        return dict_obj

    @classmethod
    def from_dict(cls, dict_obj):
        obj = cls(
            method=dict_obj['method'],
            address=dict_obj['address'],
            uri=dict_obj['uri'],
            params=dict_obj['params'],
            data=dict_obj['data'],
            headers=dict_obj['headers'],
        )
        return obj

    @staticmethod
    def sanitize_dict(dict_obj):
        # remove any key/value pairs where the value is None
        if dict_obj is not None:
            return dict((k, v) for k, v in dict_obj.items() if v is not None)
        else:
            return dict()

    def __repr__(self):
        s = list()

        kwargs = self.to_dict()
        for kw, arg in kwargs.items():
            if arg is not None:
                s.append('{kw}={arg!r}'.format(kw=kw, arg=arg))
        return '{}({})'.format(self.__class__.__name__, ', '.join(s))

    def set_method(self, method):
        self.method = method

    def get_method(self):
        return self.method

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def set_uri(self, uri):
        self.uri = uri

    def get_uri(self):
        return self.uri

    def set_params(self, params):
        self.params = params

    def get_params(self):
        return self.sanitize_dict(self.params)

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.sanitize_dict(self.data)

    def set_headers(self, headers):
        self.headers = headers

    def get_headers(self):
        return self.headers

    def get_url(self):
        return '{address}{uri}'.format(address=self.address, uri=self.uri)


class ResponseObj:
    pass


class RESTClient(object):
    """
    The RESTClient class is a base class on which api provider implementation can be build upon. The Provider class that
    inherits from this RESTClient class, should contain all the api methods provided by the api provider.

    To minimize the amount of places in memory where credentials are stored, the RESTClient class and the classes
    inheriting from the RESTClient class should not have save any credentials. Every method required that the
    credentials are passed with them. Only references in the form of a hash may be stored.
    """
    _session = None

    address = None
    uri_template = '/{endpoint}'

    def __init__(self, address=None):
        if address is not None:
            self.address = address

    @classmethod
    def _construct_uri(cls, endpoint, path_params=None):
        # Insert required values into endpoint
        if path_params is not None:
            path_params.update({'endpoint': endpoint.format(**path_params)})
        else:
            path_params = {
                'endpoint': endpoint,
            }

        # Create uri by filling in uri_template template with values from path_params
        uri = cls.uri_template.format(**path_params)

        return uri

    def _construct_request_obj(self, endpoint, method, credentials, path_params, params, data):
        uri = self._construct_uri(endpoint, path_params)
        request_obj = RequestObj(
            method=method,
            address=self.address,
            uri=uri,
            params=params,
            data=data,
        )

        if credentials is not None:
            self.sign(request_obj, credentials)

        return request_obj

    def query(self, endpoint, method='GET', credentials=None, path_params=None, params=None, data=None):
        """
        Send a query to the api host

        :param str endpoint: the endpoint path for the command you want to send to the host.
        :param str method: 'GET' or 'POST'.
        :param dict credentials: a dictionary containing key and secret values.
        :param dict path_params: a dictionary containing values required to construct uri path.
        :param dict params: Any parameters that should be added to the query url.
        :param dict data: Any form data that should be added to the request.
        :return: ResponseObj containing the response data from the host as well as formatted data.

        :Example:

        >>> r = RESTClient()
        >>> r.address = 'https://httpbin.org'
        >>> response = r.query(endpoint='get' params={'foo':'bar'})
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

        request_obj = self._construct_request_obj(
            endpoint=endpoint,
            method=method,
            credentials=credentials,
            path_params=path_params,
            params=params,
            data=data,
        )
        return request_obj
        return self.execute(request_obj)

    # @retry(exceptions=requests.exceptions.ConnectionError, tries=3, delay=0, max_delay=None, backoff=1)
    # @retry(exceptions=requests.exceptions.ReadTimeout, tries=3, delay=0, max_delay=None, backoff=1)
    def execute(self, request_obj):
        if self._session is None:
            self._session = requests.Session()

        response = self._session.request(
            method=request_obj.get_method(),
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
    def nonce():
        return str(int(time.time() * 100000))

    def sign(self, request_obj, credentials):
        """
        Signs the request object using the supplied credentials.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """
        raise NotImplementedError
