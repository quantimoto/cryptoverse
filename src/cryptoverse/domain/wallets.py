from .object_list import ObjectList


class ExchangeWallet(object):
    account = None
    label = None
    balances = None

    def __init__(self, account, label, balances):
        self.account = account
        self.label = label
        self.balances = balances


class Wallet(object):
    seed = None
    public_master_key = None

    def __init__(self, public_master_key=None, seed=None):
        self.set_seed(seed)
        self.set_public_master_key(public_master_key)

    def set_seed(self, seed):
        self.seed = seed

    def set_public_master_key(self, public_master_key):
        self.public_master_key = public_master_key


class Wallets(ObjectList):
    pass
