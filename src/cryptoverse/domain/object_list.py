from ..utilities import divide_as_decimals as divide
from ..utilities import sum_as_decimals as sum_


class ObjectList(list):

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        entries = list()
        for entry in self:
            entry_string = '\t%r' % entry
            entries.append(entry_string)
        entries = ',\n'.join(entries)
        return '{}():\n{}'.format(class_name, entries)

    def as_list(self):
        return list(self)

    def copy(self):
        return self.__class__(self.as_list())

    @property
    def first(self):
        if len(self) > 0:
            return self[0]
        else:
            return None

    @property
    def last(self):
        if len(self) > 0:
            return self[-1]
        else:
            return None

    def find(self, **kwargs):
        response = self.__class__()
        for entry in self:
            matched_kwargs = list()
            for kw in kwargs:
                if hasattr(entry, kw):
                    if getattr(entry, kw) == kwargs[kw]:
                        matched_kwargs.append(kw)
                else:
                    raise AttributeError(kw)
            if len(matched_kwargs) == len(kwargs):
                response.append(entry)
        return response

    def get(self, **kwargs):
        response = self.find(**kwargs)
        if response:
            return response.first
        return None

    def get_values(self, key):
        response = ObjectList()
        for entry in self:
            if hasattr(entry, key):
                response.append(getattr(entry, key))
            else:
                raise AttributeError(key)
        return response

    def get_sum(self, key):
        return sum_(self.get_values(key))

    def get_min(self, key):
        try:
            return min(self.get_values(key))
        except ValueError:
            return

    def get_max(self, key):
        try:
            return max(self.get_values(key))
        except ValueError:
            return

    def get_average(self, key):
        return divide(self.get_sum(key), len(self))

    def get_unique_values(self, key):
        response = ObjectList()
        for entry in self.get_values(key):
            if entry not in response:
                response.append(entry)
        return response

    def __add__(self, other):
        return self.__class__(self.as_list() + other.as_list())

    def get_unique(self):
        response = self.__class__()
        for entry in self:
            if entry not in response:
                response.append(entry)
        return response

    def __hash__(self):
        return hash(tuple(self))

    def sorted_by(self, key, reverse=False):
        return type(self)(sorted(self,
                                 key=lambda entry: getattr(entry, key, None) or entry[key],
                                 reverse=reverse))

    def __getitem__(self, index):
        if isinstance(index, int):
            return super().__getitem__(index)
        elif isinstance(index, slice):
            return self.__class__(super().__getitem__(index))
        else:
            raise TypeError("index must be int or slice")
