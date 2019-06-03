import os
import pickle


class Storage(object):
    _data_store = None
    _file = None

    def __init__(self, data=None, file=None):
        if data is not None:
            if type(data) is dict:
                self._data_store = data
            else:
                raise TypeError("Incorrect type for argument 'data': {}".format(type(data)))
        else:
            self._data_store = dict()
        if file is not None:
            self.load(file=file)

    def __str__(self):
        return self._data_store.__str__()

    def __repr__(self):
        return self._data_store.__repr__()

    def __getitem__(self, item):
        try:
            return super(self.__class__, self).__getitem__(item)
        except AttributeError:
            return self._data_store.__getitem__(item)

    def __getattr__(self, item):
        try:
            return super(self.__class__, self).__getattr__(item)
        except AttributeError:
            return self._data_store.__getitem__(item)

    def __setitem__(self, key, value):
        response = self._data_store.__setitem__(key, value)
        return response

    def get(self, k, default):
        return self._data_store.get(k, default)

    def load(self, file=None):
        file = file or self._file
        if file is not None:
            filepath = os.path.abspath(os.path.expanduser(file))

            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'rb') as infile:
                        contents = pickle.load(infile)
                    self._data_store = contents
                except EOFError:
                    self._data_store = dict()
            if self._file != file:
                self._file = file

    def save(self, file=None):
        file = file or self._file
        if file is not None:
            filepath = os.path.abspath(os.path.expanduser(file))

            with open(filepath, 'wb') as outfile:
                pickle.dump(obj=self._data_store, file=outfile)
            if self._file != file:
                self._file = file

    def clear(self):
        self._data_store = dict()

    def keys(self):
        return self._data_store.keys()

    def __contains__(self, item):
        return self._data_store.__contains__(item)

    def __delitem__(self, key):
        return self._data_store.__delitem__(key)
