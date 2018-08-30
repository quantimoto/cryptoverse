import hashlib
import sys
import time
from functools import wraps
from math import floor

from termcolor import cprint

from cryptoverse.base.rest.response import ResponseObj


class Memoize(object):
    def __init__(self, expires):
        self.expires = expires
        self.store = {}

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            h = hashlib.sha1()
            key = str((args, kwargs)).encode('utf-8')
            h.update(key)
            key_hash = h.hexdigest()

            response = None
            if key_hash in self.store.keys():
                (timestamp, response), = self.store[key_hash].items()
                if timestamp < time.time() - self.expires:
                    response = None

            if response is None:
                response = func(*args, **kwargs)
                self.store[key_hash] = dict()
                self.store[key_hash][time.time()] = response

            return response

        return wrapper


class RateLimit(object):
    def __init__(self, calls=60, period=60):
        self.calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = max(1, max(period, -period))
        self.delay = float(self.period) / float(self.calls)
        self.last_call = None

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            if self.last_call is None:
                remaining = 0
            else:
                elapsed = now - self.last_call
                remaining = self.delay - elapsed

            if remaining > 0:
                time.sleep(remaining)

            response = func(*args, **kwargs)

            self.last_call = time.time()
            return response

        return wrapper


class Backoff(object):
    def __init__(self, exception, wait=10):
        self.wait = wait
        self.exception = exception

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = None
            successful = False
            while not successful:
                try:
                    response = func(*args, **kwargs)
                    successful = True
                except self.exception:
                    cprint('{}: {}'.format(time.time(), self.exception.__name__), 'red')
                    time.sleep(self.wait)

            return response

        return wrapper


def formatter(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        response = func(*args, **kwargs)
        response_obj = ResponseObj(response)
        return response_obj

    return wrapped
