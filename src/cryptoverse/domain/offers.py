from .object_list import ObjectList


class Offer(object):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        pass


class Offers(ObjectList):
    pass
