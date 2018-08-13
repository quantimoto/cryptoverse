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
            kwargstrings.append("{}='{}..{}'".format(kw, self.__dict__[kw][:3], self.__dict__[kw][-3:]))
        return '{}({})'.format(class_name, ', '.join(kwargstrings))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.key, self.secret) == (other.key, other.secret):
                return True
        return False

    def __hash__(self):
        return hash((self.key, self.secret))

    def set_key(self, value):
        self.key = value

    def set_secret(self, value):
        self.secret = value

    def get_key(self):
        return self.key

    def get_secret(self):
        return self.secret
