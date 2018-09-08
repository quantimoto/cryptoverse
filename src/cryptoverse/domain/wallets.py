from .object_list import ObjectList


class ExchangeWallet(object):
    account = None
    label = None
    balances = None

    def __init__(self, account, label, balances):
        self.account = account
        self.label = label
        self.balances = balances

    def __repr__(self):
        kwargs = 'label={}'.format(self.label)
        return '{}({}):\n{}'.format(self.__class__.__name__, kwargs, self.balances)

    @property
    def instruments(self):
        return self.balances.instruments


class Wallet(object):
    seed = None
    public_master_key = None
    instrument = None

    def __init__(self, instrument=None, public_master_key=None, seed=None):
        self.instrument = instrument
        self.seed = seed
        self.public_master_key = public_master_key


class Wallets(ObjectList):
    def __getitem__(self, item):
        if type(item) is int:
            return super(self.__class__, self).__getitem__(item)
        else:
            return self.find(label=item).first

    @property
    def balances(self):
        from .balances import Balances
        result = Balances()
        for entry in self:
            result = result + entry.balances
        return result

    @property
    def instruments(self):
        from .instruments import Instruments
        result = Instruments()
        for entry in self:
            result = result + entry.instruments
        return result
