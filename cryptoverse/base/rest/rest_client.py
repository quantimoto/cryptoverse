import requests
from retry import retry


class ResponseObj:
    pass


class RESTClient(object):
    session = None

    base_url = None
    endpoint = None

    def public_request(self, command, version=1, params=None):
        if self.base_url is not None and self.endpoint is not None:
            url = '{}{}'.format(self.base_url, self.endpoint)
            self.request(
                method='GET',
                url=url,
            )
            return response

    @staticmethod
    def nonce():
        return str(long(time.time() * 100000))

    def authenticated_request(self, command, version=1, params=None):
        if self.base_url is not None and self.endpoint is not None:
            url = '{}{}'.format(self.base_url, self.endpoint)
            self.request(
                method='POST',
                url=url,
            )
            return response

    @retry(exceptions=requests.exceptions.ReadTimeout, tries=3, delay=0, max_delay=None, backoff=1)
    def request(self, method, url, params=None, data=None, headers=None, timeout=None, allow_redirects=True,
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

