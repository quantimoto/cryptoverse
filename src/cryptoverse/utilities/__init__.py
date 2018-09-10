from decimal import Decimal


def strip_none(data):
    if isinstance(data, dict):
        result = {k: strip_none(v) for k, v in data.items() if k is not None and v is not None}
    elif isinstance(data, list):
        result = [strip_none(item) for item in data if item is not None]
    elif isinstance(data, tuple):
        result = tuple(strip_none(item) for item in data if item is not None)
    elif isinstance(data, set):
        result = {strip_none(item) for item in data if item is not None}
    else:
        result = data

    if result is not None:
        return result


def strip_empty(data):
    if isinstance(data, dict):
        result = {kw: strip_empty(item) for kw, item in data.items() if
                  not hasattr(item, '__len__') or (hasattr(item, '__len__') and len(item) > 0)}
    elif isinstance(data, list):
        result = [strip_empty(item) for item in data if
                  not hasattr(item, '__len__') or (hasattr(item, '__len__') and len(item) > 0)]
    elif isinstance(data, tuple):
        result = tuple(strip_empty(item) for item in data if
                       not hasattr(item, '__len__') or (hasattr(item, '__len__') and len(item) > 0))
    elif isinstance(data, set):
        result = {strip_empty(item) for item in data if
                  not hasattr(item, '__len__') or (hasattr(item, '__len__') and len(item) > 0)}
    else:
        result = data

    if hasattr(result, '__len__'):
        if len(result) > 0:
            return result
        else:
            return None
    else:
        return result


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


def multiply_as_decimals(a, b):
    """
    >>> a = 1.1
    >>> b = 2.2
    >>> a * b
    2.4200000000000004
    >>> multiply_as_decimals(a, b)
    2.42
    """
    return float(Decimal(str(float(a))) * Decimal(str(float(b))))


def divide_as_decimals(a, b):
    """
    >>> a = 2.42
    >>> b = 2.2
    >>> a / b
    1.0999999999999999
    >>> multiply_as_decimals(a, b)
    1.1
    """
    return float(Decimal(str(float(a))) / Decimal(str(float(b))))


def add_as_decimals(a, b):
    """
    >>> a = 1.1
    >>> b = 2.2
    >>> a + b
    3.3000000000000003
    >>> multiply_as_decimals(a, b)
    3.3
    """
    return float(Decimal(str(float(a))) + Decimal(str(float(b))))


def subtract_as_decimals(a, b):
    """
    >>> a = 3.3
    >>> b = 2.2
    >>> a - b
    1.0999999999999996
    >>> subtract_as_decimals(a, b)
    1.1
    """
    return float(Decimal(str(float(a))) - Decimal(str(float(b))))
