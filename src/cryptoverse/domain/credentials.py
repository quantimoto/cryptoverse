from hashlib import sha256


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
