from unittest import TestCase

from cryptoverse.utilities import strip_none


class TestStripNone(TestCase):
    def test_strip_none(self):
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
            'foo4': {
                'foo': 'bar',
            },
            'foo5': {},
            'foo6': {},
            'foo7': ['foo', 'bar'],
            'foo8': ['foo'],
            'foo9': [],
            'foo10': [],
        }
        self.assertEqual(expected, strip_none(data))
