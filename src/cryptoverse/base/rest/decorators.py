import hashlib
import json
import logging
import os
import sys
import tempfile
import time
from functools import wraps
from math import floor

from cryptoverse.exceptions import ExchangeMaxRetryException
from .response import ResponseObj

logger = logging.getLogger(__name__)


class Memoize(object):
    def __init__(self, expires, persistent=False, instance_bound=True):
        self.expires = expires
        self.store = dict()
        self.persistent = persistent
        self.instance_bound = instance_bound

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ', '.join(['{!r}'.format(arg) for arg in args])
            if self.instance_bound is False:
                args_str = ', '.join(args[1:])
            kwargs_str = ', '.join(['{}={!r}'.format(kw, arg) for kw, arg in kwargs.items()])

            key = '{}.{}({})'.format(
                func.__module__,
                func.__name__,
                ', '.join([x for x in [args_str, kwargs_str] if x]),
            ).encode('UTF-8')

            h = hashlib.sha1()
            h.update(key)
            key_hash = h.hexdigest()

            filepath = os.path.join(tempfile.gettempdir(), 'cryptoverse_{}'.format(key_hash))

            try:
                cache = json.load(open(filepath, 'r'))
            except FileNotFoundError:
                cache = dict()

            response = None
            now = time.time()
            if key_hash in self.store.keys():
                timestamp = max(self.store[key_hash].keys())
                stored_response = self.store[key_hash][timestamp]
                if float(timestamp) > now - self.expires:
                    response = stored_response
                    logger.debug('Returning stored response from memory for: {}'.format(key))
            elif cache:
                timestamp = max(cache.keys())
                stored_response = cache[timestamp]
                if float(timestamp) > now - self.expires:
                    response = stored_response
                    logger.debug('Returning stored response from disk for: {}'.format(key))

            if response is None:
                now = time.time()
                response = func(*args, **kwargs)

                # Store response in memory
                self.store[key_hash] = dict()
                self.store[key_hash][now] = response

                # Store response to disk
                cache = {now: response}
                json.dump(cache, open(filepath, 'w'))

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
                logger.debug('Sleeping for {} seconds to respect ratelimit for: {}'.format(remaining, func))
                time.sleep(remaining)

            response = func(*args, **kwargs)

            self.last_call = time.time()
            return response

        return wrapper


class Retry(object):
    def __init__(self, exception, wait=10, max_tries=None):
        self.exception = exception
        self.wait = wait
        self.max_tries = max_tries

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = None
            successful = False
            counter = 0
            while not successful:
                try:
                    response = func(*args, **kwargs)
                    successful = True
                except self.exception as e:
                    counter += 1
                    logger.warning(
                        '{} {}: {} - {}({} {})'.format(time.time(), self.exception.__name__, e, func, args, kwargs))
                    if self.max_tries is not None and self.max_tries == counter:
                        raise ExchangeMaxRetryException
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
