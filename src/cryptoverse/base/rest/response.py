class ResponseObj(object):
    """
    The ResponseObj contains the response from a server, as well as the original RequestObj and the raw response that
    the requests library returns.
    """

    raw_response = None
    formatted_response = None

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.formatted_response = self._format_raw_response(raw_response)

    @staticmethod
    def _format_raw_response(raw_response):
        json_response = raw_response.json()
        formatted_response = json_response
        return formatted_response

    def copy(self):
        return self.formatted_response.copy()

    def get(self, k, d=None):
        return self.formatted_response.get(k, d)

    def items(self):
        return self.formatted_response.items()

    def keys(self):
        return self.formatted_response.keys()

    def values(self):
        return self.formatted_response.values()

    def __contains__(self, *args, **kwargs):
        return self.formatted_response(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.formatted_response(*args, **kwargs)

    def __getitem__(self, item):
        return self.formatted_response.__getitem__(item)

    def __iter__(self, *args, **kwargs):
        return self.formatted_response.__iter__(*args, **kwargs)

    def __repr__(self):
        return repr(self.formatted_response)
