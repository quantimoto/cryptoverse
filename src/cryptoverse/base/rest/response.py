class ResponseObj(object):
    """
    The ResponseObj contains the response from a server, as well as the original RequestObj and the raw response that
    the requests library returns.
    """

    raw = None
    decoded_response = None

    def __init__(self, response):
        self.raw = response
        self.decoded_response = self._decode_response(response)

    @staticmethod
    def _decode_response(raw_response):
        json_response = raw_response.json()
        decoded_response = json_response
        return decoded_response

    def as_obj(self):
        return self.decoded_response

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
        return self.decoded_response.__contains__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.decoded_response.__eq__(*args, **kwargs)

    def __getitem__(self, item):
        return self.decoded_response.__getitem__(item)

    def __iter__(self, *args, **kwargs):
        return self.decoded_response.__iter__(*args, **kwargs)

    def __repr__(self):
        return self.decoded_response.__repr__()

    def __str__(self):
        return self.decoded_response.__str__()

    def __len__(self):
        return self.decoded_response.__len__()
