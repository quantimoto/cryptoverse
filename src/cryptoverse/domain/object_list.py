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

    def first(self):
        return self[0]

    def last(self):
        return self[-1]

    def find(self, **kwargs):
        response = self.__class__()
        for entry in self:
            matched_kwargs = list()
            for kw in kwargs.keys():
                if hasattr(entry, kw):
                    if getattr(entry, kw) == kwargs[kw]:
                        matched_kwargs.append(kw)
                else:
                    raise AttributeError(kw)
            if len(matched_kwargs) == len(kwargs):
                response.append(entry)
        return response

    def get(self, **kwargs):
        return self.find(**kwargs).first()

    def get_values(self, key):
        response = ObjectList()
        for entry in self:
            if hasattr(entry, key):
                response.append(getattr(entry, key))
            else:
                raise AttributeError(key)
        return response

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
