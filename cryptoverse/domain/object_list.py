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
