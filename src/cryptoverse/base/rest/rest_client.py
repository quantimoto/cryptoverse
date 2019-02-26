import logging
import time

from requests import request

from .request import RequestObj

logger = logging.getLogger(__name__)


class RESTClient(object):
    """
    The RESTClient class is a base class on which api-provider implementation can be build upon. The Provider class that
    inherits from this RESTClient class, should contain all the api methods provided by the api provider.

    To minimize the amount of places in memory where credentials are stored, the RESTClient class and the classes
    inheriting from the RESTClient class should not have save any credentials. Every method required that the
    credentials are passed with them. Only references in the form of a hash may be stored.

    Methods here are a direct translation from python to the exchange's available methods. Method names and parameters
    reflect those in the official documentation as much as possible. Response is kept in-tact and no additional logic is
    executed in this obj.
    """
    _timeout = (60, 60)  # Connect, Read

    scheme = 'https'
    host = None

    def __init__(self, host=None, scheme=None):
        if host is not None:
            self.host = host
        if scheme is not None:
            self.scheme = scheme

    def __eq__(self, other):
        if type(self) is type(other):
            if (self.scheme, self.host) == (other.scheme, other.host):
                return True
        return False

    def __hash__(self):
        return hash((self.scheme, self.host))

    def _create_request(self, path, method, credentials, path_params, query_params, data):
        # Insert path parameters into path
        if path_params is not None:
            path = path.format(**path_params)

        # Create object containing request arguments
        request_obj = RequestObj(
            method=method,
            host=self.host,
            path=path,
            params=query_params,
            data=data,
            scheme=self.scheme,
        )

        # Add a signature to the request object if required
        if credentials is not None:
            self.sign(request_obj, credentials)

        return request_obj

    def request(self, path, method='GET', credentials=None, path_params=None, query_params=None, data=None):
        """
        Send a query to the api host

        :param str path: the endpoint path for the command you want to send to the host.
        :param str method: 'GET' or 'POST'.
        :param dict credentials: a dictionary containing key and secret values.
        :param dict path_params: a dictionary containing values required to construct url path.
        :param dict query_params: Any parameters that should be added to the query url.
        :param dict data: Any form data that should be added to the request.
        :return: ResponseObj containing the response data from the host as well as formatted data.

        :Example:

        >>> r = RESTClient()
        >>> r.address = 'https://httpbin.org'
        >>> response = r.request(endpoint='get' query_params={'foo':'bar'})
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

        request_obj = self._create_request(
            path=path,
            method=method,
            credentials=credentials,
            path_params=path_params,
            query_params=query_params,
            data=data,
        )
        logger.debug("Sending request: {}".format(request_obj))
        response = self._send_request(request_obj)
        logger.debug("Received response")

        return response

    def _send_request(self, request_obj):
        response = request(
            method=request_obj.method,
            url=request_obj.url,
            params=request_obj.params,
            data=request_obj.data,
            json=request_obj.json,
            headers=request_obj.headers,
            timeout=self._timeout,
            allow_redirects=False,
            verify=True,
        )

        return response

    # Authentication methods

    @staticmethod
    def nonce():
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(time.time() * 1000000))

    def sign(self, request_obj, credentials):
        """
        Signs the request object using the supplied credentials.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """
        raise NotImplementedError
