import hashlib
import sys
import time
from functools import wraps
from math import floor

from termcolor import cprint


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

            result = None
            if key_hash in self.store.keys():
                (timestamp, result), = self.store[key_hash].items()
                if timestamp < time.time() - self.expires:
                    result = None

            if result is None:
                result = func(*args, **kwargs)
                self.store[key_hash] = dict()
                self.store[key_hash][time.time()] = result

            return result

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

            result = func(*args, **kwargs)

            self.last_call = time.time()
            return result

        return wrapper


class Backoff(object):
    def __init__(self, exception, wait=10):
        self.wait = wait
        self.exception = exception

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            successful = False
            while not successful:
                try:
                    result = func(*args, **kwargs)
                    successful = True
                except self.exception:
                    cprint(time.time(), 'red')
                    cprint(self.exception, 'red')
                    time.sleep(self.wait)

            return result

        return wrapper
