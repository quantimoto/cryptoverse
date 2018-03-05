from hashlib import sha256

from .object_list import ObjectList


class Credentials(object):
    key = None
    secret = None

    def __init__(self, key=None, secret=None):
        self.set_key(value=key)
        self.set_secret(value=secret)

    def __repr__(self):
        class_name = self.__class__.__name__
        kwargstrings = list()
        for kw in ['key', 'secret']:
            kwargstrings.append('{}={}'.format(kw, self.__dict__[kw]))
        return '{}({})'.format(class_name, ', '.join(kwargstrings))

    def set_key(self, value):
        self.key = value

    def set_secret(self, value):
        self.secret = value

    def get_key(self):
        return self.key

    def get_secret(self):
        return self.secret

    def get_hash(self):
        hash_ = sha256()

        key = self.get_key()
        if key is not None:
            key = bytes(self.get_key(), 'utf-8')
            hash_.update(key)

        secret = self.get_secret()
        if secret is not None:
            secret = bytes(self.get_secret(), 'utf-8')
            hash_.update(secret)

        return hash_.hexdigest()

    def display_hash(self):
        hash_ = self.get_hash()
        parts_size = 3
        return '{}..{}'.format(hash_[:parts_size], hash_[-parts_size:])


class Account(object):
    exchange = None
    credentials = None
    label = None

    __all__ = ['orders', 'trades', 'positions', 'offers', 'lends', 'balances', 'deposits', 'withdraws']

    def __init__(self, exchange=None, credentials=None, label=None):
        self.set_exchange(exchange)
        self.set_credentials(credentials)
        self.set_label(label)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        kwargstrings = list()
        for kw in ['exchange', 'credentials', 'label']:
            if kw in self.__dict__.keys():
                arg = self.__dict__[kw]
                if arg is not None:
                    kwargstrings.append('{}={}'.format(kw, arg))
        return '{}({})'.format(class_name, ', '.join(kwargstrings))

    def set_exchange(self, exchange):
        self.exchange = exchange

    def set_credentials(self, credentials):
        self.credentials = credentials

    def set_label(self, label):
        self.label = label

    def get_exchange(self):
        return self.exchange

    def get_credentials(self):
        return self.credentials

    def get_label(self):
        return self.label

    def orders(self):
        raise NotImplementedError

    def trades(self):
        raise NotImplementedError

    def positions(self):
        raise NotImplementedError

    def offers(self):
        raise NotImplementedError

    def lends(self):
        raise NotImplementedError

    def balances(self):
        raise NotImplementedError

    def deposits(self):
        raise NotImplementedError

    def withdraws(self):
        raise NotImplementedError


class Accounts(ObjectList):
    pass
