class ResponseObj:
    """
    The ResponseObj contains the response from a server, as well as the original RequestObj and the raw response that
    the requests library returns.
    """

    request_obj = None
    raw_response = None
