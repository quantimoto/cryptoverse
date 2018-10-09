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
    pass
