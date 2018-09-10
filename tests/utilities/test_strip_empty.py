from unittest import TestCase

from cryptoverse.utilities import strip_empty


class TestStripEmpty(TestCase):
    def test_strip_empty(self):
        data = {
            'foo': 'bar',
            'foo1': True,
            'foo2': False,
            'foo3': None,
            'foo4': {
                'foo': 'bar',
                'foo1': None,
            },
            'foo5': {
                'foo': None,
                'bar': None,
            },
            'foo6': {},
            'foo7': ['foo', 'bar'],
            'foo8': ['foo', None],
            'foo9': [None, None],
            'foo10': [],
        }
        expected = {
            'foo': 'bar',
            'foo1': True,
            'foo2': False,
            'foo3': None,
            'foo4': {
                'foo': 'bar',
                'foo1': None,
            },
            'foo5': {
                'foo': None,
                'bar': None,
            },
            'foo7': ['foo', 'bar'],
            'foo8': ['foo', None],
            'foo9': [None, None],
        }
        self.assertEqual(expected, strip_empty(data))
        data = {}
        expected = None
        self.assertEqual(expected, strip_empty(data))
