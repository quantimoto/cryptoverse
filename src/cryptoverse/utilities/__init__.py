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
