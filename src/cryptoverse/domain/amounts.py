from cryptoverse.domain.object_list import ObjectList


class Amount:
    value = None
    instrument = None

    def __init__(self, value=0, instrument=None):
        self.value = float(value)
        self.instrument = instrument

    def __repr__(self):
        return '{:.8f} {!s}'.format(self.value, self.instrument)


class Amounts(ObjectList):

    def __getitem__(self, item):
        if type(item) is int:
            return super(self.__class__, self).__getitem__(item)
        elif type(item) is str:
            for entry in self:
                if entry.instrument == item:
                    return entry

    @property
    def instruments(self):
        return self.get_unique_values('instrument')
