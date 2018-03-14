import requests
from retry import retry


class ResponseObj:
    pass


class RESTClient(object):
    session = None

    base_url = None
    public_endpoint = None
    authenticated_endpoint = None

    def public_query(self, command, version=1, params=None):
        if self.base_url is not None and self.public_endpoint is not None:
            url = '{}{}'.format(self.base_url, self.public_endpoint)
            response = self.request(
                method='GET',
                url=url,
            )
            return response

    @staticmethod
    def nonce():
        return str(long(time.time() * 100000))

    def authenticated_query(self, key, secret, command, version=1, params=None):
        if self.base_url is not None and self.public_endpoint is not None:
            url = '{}{}'.format(self.base_url, self.public_endpoint)
            response = self.request(
                method='POST',
                url=url,
            )
            return response

    @retry(exceptions=requests.exceptions.ConnectionError, tries=3, delay=0, max_delay=None, backoff=1)
    @retry(exceptions=requests.exceptions.ReadTimeout, tries=3, delay=0, max_delay=None, backoff=1)
    def query(self, method, url, params=None, data=None, headers=None, timeout=None, allow_redirects=True,
              verify=None):
        if self.session is None:
            self.session = requests.Session()

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=verify,
        )

        return response
