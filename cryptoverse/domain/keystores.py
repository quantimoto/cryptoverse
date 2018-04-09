import getpass
import os

import libkeepass


class Keepassx(dict):
    """
    >>> keys = Keepassx('test-keys', 'test')
    >>> keys.bitfinex.empty
    {'secret': '...',
    'key': '...'}
    """
    filename = None

    def __init__(self, filename='default', password=None):
        self.set_filename(filename)
        data = self.from_file(filename, password)
        super(self.__class__, self).__init__(data)

    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = list()
        attributes.append('{key}={value!r}'.format(key='filename', value=self.filename))
        attributes.append('{key}={value!r}'.format(key='password', value='***'))
        return '{class_name}({attrs})'.format(class_name=class_name, attrs=', '.join(attributes))

    def set_filename(self, filename):
        self.filename = filename

    @classmethod
    def from_file(cls, filename, password=None):
        if not os.path.isfile(filename) and '/' not in filename:
            filename = os.path.join('~/.cryptoverse', '{}.kdbx'.format(filename))
        filename = os.path.abspath(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise IOError("No such file or directory: '{}'".format(filename))

        basename = os.path.basename(filename)
        environ_key = '{}_PASSWORD'.format(basename.upper().replace('.', '_').replace('-', '_'))

        if password is None and environ_key in os.environ.keys():
            password = os.environ[environ_key]
        elif password is None:
            password = getpass.getpass()

        data = {}
        with libkeepass.open(filename, password=password) as kdb:
            for group in kdb.obj_root.Root.Group.findall('Group'):
                data[group.Name] = {}
                for entry in group.findall('Entry'):
                    title, username, password = None, None, None
                    for string in entry.findall('String'):
                        if string.Key == 'Title':
                            title = string.Value
                        if string.Key == 'UserName':
                            username = string.Value
                        if string.Key == 'Password':
                            password = string.Value
                    data[group.Name][title] = {
                        'key': str(username),
                        'secret': str(password),
                    }
        return data

    def groups(self):
        return list(self.keys())
