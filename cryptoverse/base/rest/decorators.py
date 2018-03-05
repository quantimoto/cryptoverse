import functools
from time import sleep


def rate_limit(amount=90, timespan=60):
    """
    Delays execution when previous call was within rate-limit
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sleep(float(timespan) / float(amount))  # TODO: only sleep if same function was called within rate-limit
            return func(*args, **kwargs)

        return wrapper

    return decorator
