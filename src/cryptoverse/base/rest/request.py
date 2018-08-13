class RequestObj:
    """
    The RequestObj stores all parameters required to do an api request. It can be serialized and stored, in order for a
    different host to do the actual request to the provider. The RequestObj can be updated with a new signature, in case
    a previous request failed.

    Credentials are not stored in the RequestObj. When a request has failed, the host that retries it needs to have
    access to the credentials itself.
    """

    method = None
    url = None
    params = None
    data = None
    headers = None

    def __init__(self, method=None, url=None, params=None, data=None, headers=None):
        self.set_method(method)
        self.set_url(url)
        self.set_params(params)
        self.set_data(data)
        self.set_headers(headers)

    def as_dict(self):
        dict_obj = {
            'method': self.get_method(),
            'url': self.get_url(),
            'params': self.get_params(),
            'data': self.get_data(),
            'header': self.get_headers(),
        }
        return dict_obj

    @classmethod
    def from_dict(cls, dict_obj):
        obj = cls(
            method=dict_obj['method'],
            url=dict_obj['url'],
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

        kwargs = self.as_dict()
        for kw, arg in kwargs.items():
            if arg is not None:
                s.append('{kw}={arg!r}'.format(kw=kw, arg=arg))
        return '{}({})'.format(self.__class__.__name__, ', '.join(s))

    def set_method(self, method):
        self.method = method

    def get_method(self):
        return self.method

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_params(self, params):
        if not params:
            self.params = dict()
        else:
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
