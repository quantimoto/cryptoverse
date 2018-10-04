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
            )

            h = hashlib.sha1()
            h.update(key.encode('UTF-8'))
            key_hash = h.hexdigest()

            response = None
            now = time.time()
            if key_hash in self.store.keys():
                timestamp = max(self.store[key_hash].keys())
                stored_response = self.store[key_hash][timestamp]
                if float(timestamp) >= now - self.expires:
                    response = stored_response
                    logger.info('Returning stored response from memory for: {} {}'.format(key_hash, key))
            elif self.persistent:
                filepath = os.path.join(tempfile.gettempdir(), 'cryptoverse_{}'.format(key_hash))
                if os.path.isfile(filepath):
                    cache = json.load(open(filepath, 'r'))
                    timestamp = max(cache.keys())
                    stored_response = cache[timestamp]
                    if float(timestamp) >= now - self.expires:
                        response = stored_response
                        logger.info('Returning stored response from disk for: {} {}'.format(key_hash, key))

            if response is None:
                now = time.time()
                logger.info('Getting response from function for: {} {}'.format(key_hash, key))
                response = func(*args, **kwargs)

                # Store response in memory
                self.store[key_hash] = dict()
                self.store[key_hash][now] = response

                if self.persistent:
                    # Store response to disk
                    if hasattr(response, 'decoded_response'):
                        cache = {now: response.decoded_response}
                    else:
                        cache = {now: response}

                    filepath = os.path.join(tempfile.gettempdir(), 'cryptoverse_{}'.format(key_hash))
                    json.dump(cache, open(filepath, 'w'))

            return response

        return wrapper


class RateLimit(object):
    def __init__(self, calls=60, period=60, sleep=False, min_delay=0):
        self.calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = max(1, max(period, -period))
        self.sleep = sleep

        self.min_delay = max(min_delay, -min_delay)
        self.sleep_time = float(self.period) / float(self.calls)
        self.first_call = None
        self.last_call = None
        self.counter = 0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            delay = 0
            if self.sleep is True:
                if self.last_call is not None:
                    elapsed_time = now - self.last_call
                    delay = self.sleep_time - elapsed_time
            else:
                if self.counter >= self.calls:
                    elapsed_time = now - self.first_call
                    delay = self.period - elapsed_time
                    if delay > 0:
                        logger.info('{} calls within {} seconds.'.format(self.counter, elapsed_time))
                    self.counter = 0
                    self.first_call = None

            if delay - self.min_delay > 0:
                logger.info(
                    'Sleeping for {:.3f} seconds to respect ratelimit for: {}.{}({})'.format(
                        delay,
                        func.__module__,
                        func.__name__,
                        ', '.join([x for x in [
                            ', '.join(['{!r}'.format(arg) for arg in args]),
                            ', '.join(['{}={!r}'.format(kw, arg) for kw, arg in kwargs.items()])
                        ] if x]),
                    )
                )

            delay = max(delay, self.min_delay)
            time.sleep(delay)

            self.first_call = self.first_call or time.time()

            response = func(*args, **kwargs)

            self.last_call = time.time()
            self.counter += 1

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
                except self.exception:
                    counter += 1
                    logger.warning(
                        '{} - {}: {}.{}({})'.format(
                            time.time(),
                            self.exception.__name__,
                            func.__module__,
                            func.__name__,
                            ', '.join([x for x in [
                                ', '.join(['{!r}'.format(arg) for arg in args]),
                                ', '.join(['{}={!r}'.format(kw, arg) for kw, arg in kwargs.items()])
                            ] if x]),
                        )
                    )
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
