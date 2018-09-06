class ResponseObj(object):
    """
    The ResponseObj contains the response from a server, as well as the original RequestObj and the raw response that
    the requests library returns.
    """

    raw_response = None
    decoded_response = None

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.decoded_response = self._decode_raw_response(raw_response)

    @staticmethod
    def _decode_raw_response(raw_response):
        json_response = raw_response.json()
        decoded_response = json_response
        return decoded_response

    def copy(self):
        return self.decoded_response.copy()

    def get(self, k, d=None):
        return self.decoded_response.get(k, d)

    def items(self):
        return self.decoded_response.items()

    def keys(self):
        return self.decoded_response.keys()

    def values(self):
        return self.decoded_response.values()

    def __contains__(self, *args, **kwargs):
        return self.decoded_response(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.decoded_response(*args, **kwargs)

    def __getitem__(self, item):
        return self.decoded_response.__getitem__(item)

    def __iter__(self, *args, **kwargs):
        return self.decoded_response.__iter__(*args, **kwargs)

    def __repr__(self):
        return repr(self.decoded_response)
