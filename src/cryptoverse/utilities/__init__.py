def strip_none(data):
    if isinstance(data, dict):
        results = {k: strip_none(v) for k, v in data.items() if k is not None and v is not None}
    elif isinstance(data, list):
        results = [strip_none(item) for item in data if item is not None]
    elif isinstance(data, tuple):
        results = tuple(strip_none(item) for item in data if item is not None)
    elif isinstance(data, set):
        results = {strip_none(item) for item in data if item is not None}
    else:
        results = data

    if results:
        return results


def strip_empty(data):
    if isinstance(data, dict):
        results = {k: strip_empty(v) for k, v in data.items() if k and v}
    elif isinstance(data, list):
        results = [strip_empty(item) for item in data if item]
    elif isinstance(data, tuple):
        results = tuple(strip_empty(item) for item in data if item)
    elif isinstance(data, set):
        results = {strip_empty(item) for item in data if item}
    else:
        results = data

    if results:
        return results


def round_down(x, ndigits=8):
    """
    >>> round(1.987654321, ndigits=3)
    1.988
    >>> round_down(1.987654321, ndigits=3)
    1.987
    """
    if x is not None:
        split = (('%.' + str(ndigits + 1) + 'f') % x).split('.')  # prevent scientific notation
        truncated = '.'.join([split[0], split[1][:ndigits]])
        return float(truncated)
    else:
        return None


def round_significant(x, ndigits=5):
    """
    >>> round_significant(1987.654321, ndigits=5)
    1987.7
    >>> round_significant(198.7654321, ndigits=5)
    198.77
    >>> round_significant(19.87654321, ndigits=5)
    19.877
    >>> round_significant(1.987654321, ndigits=5)
    1.9877
    >>> round_significant(0.1987654321, ndigits=5)
    0.19877
    >>> round_significant(0.01987654321, ndigits=5)
    0.019877
    """
    if x is not None and ndigits > 0:
        rounded = ('%.' + str(int(ndigits)) + 'g') % x
        return float(rounded)
    else:
        return None


def remove_empty(kwargs):
    kwargs = kwargs.copy()
    for k, v in kwargs.copy().items():
        if v is None:
            del kwargs[k]
    return kwargs


def remove_keys(kwargs, keys):
    kwargs = kwargs.copy()
    for k in kwargs.copy().keys():
        if k in keys:
            del kwargs[k]
    return kwargs
