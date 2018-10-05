class RequestObj:
    """
    The RequestObj stores all parameters required to do an api request. It can be serialized and stored, in order for a
    different host to do the actual request to the provider. The RequestObj can be updated with a new signature, in case
    a previous request failed.

    Credentials are not stored in the RequestObj. When a request has failed, the host that retries it needs to have
    access to the credentials itself.
    """

    method = None
    scheme = None
    host = None
    path = None
    _params = None
    _data = None
    _headers = None

    data_as_json = None

    def __init__(self, method=None, host=None, path=None, params=None, data=None, headers=None, scheme='https', data_as_json=False):
        self.method = method
        self.host = host
        self.path = path
        self.params = params
        self.data = data
        self.headers = headers
        self.scheme = scheme
        self.data_as_json = data_as_json

    def __repr__(self):
        s = list()

        kwargs = self.as_dict()
        for kw, arg in kwargs.items():
            if arg is not None:
                s.append('{kw}={arg!r}'.format(kw=kw, arg=arg))
        return '{}({})'.format(self.__class__.__name__, ', '.join(s))

    def as_dict(self):
        dict_obj = {
            'method': self.method,
            'host': self.host,
            'path': self.path,
            'params': self.params,
            'data': self.data,
            'header': self.headers,
            'data_as_json': self.data_as_json,
        }
        return dict_obj

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(
            method=dict_obj['method'],
            host=dict_obj['host'],
            path=dict_obj['path'],
            params=dict_obj['params'],
            data=dict_obj['data'],
            headers=dict_obj['headers'],
            scheme=dict_obj['scheme'],
            data_as_json=dict_obj['data_as_json'],
        )

    @staticmethod
    def sanitize_dict(dict_obj):
        # remove any key/value pairs where the value is None
        if dict_obj is not None:
            return dict((k, v) for k, v in dict_obj.items() if v is not None)
        else:
            return dict()

    @property
    def url(self):
        url_params = {
            'scheme': self.scheme,
            'host': self.host,
            'path': self.path,
        }
        return '{scheme}://{host}/{path}'.format(**url_params)

    @property
    def params(self):
        return self.sanitize_dict(self._params).copy()

    @params.setter
    def params(self, value):
        if not value and type(value) is not dict:
            self._params = dict()
        else:
            self._params = value

    @property
    def data(self):
        if self.data_as_json is True:
            return None
        return self.sanitize_dict(self._data).copy()

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def json(self):
        if self.data_as_json is not True:
            return None
        return self.sanitize_dict(self._data).copy()

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value
