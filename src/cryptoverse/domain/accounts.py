from .balances import Balance, Balances
from .credentials import Credentials
from .object_list import ObjectList
from .offers import Offer, Offers
from .orders import Order, Orders
from .wallets import ExchangeWallet, Wallets


class Account(object):
    _exchange = None
    label = None

    def __init__(self, exchange=None, credentials=None, label=None):
        self.exchange = exchange
        self.credentials = credentials
        self.label = label

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = list()
        for key in ['exchange', 'credentials', 'label']:
            value = getattr(self, key)
            if value is not None:
                attributes.append('{}={!r}'.format(key, value))
        return '{class_name}({attributes})'.format(class_name=class_name, attributes=', '.join(attributes))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.exchange, self.credentials) == (other.exchange, other.credentials):
                return True
        return False

    def __hash__(self):
        return hash((self.exchange, self.credentials))

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        if value is not None:
            self._exchange = value.copy()

    @property
    def credentials(self):
        if self.exchange:
            return self.exchange.interface.rest_client.credentials
        else:
            return None

    @credentials.setter
    def credentials(self, value):
        if self.exchange is not None and value is not None:
            self.exchange.interface.rest_client.credentials = value

    def fees(self):
        return self.exchange.interface.get_account_fees()

    def orders(self, market=None):
        return self.exchange.interface.get_account_orders(market=market)

    def trades(self, market):
        return self.exchange.interface.get_account_trades(market=market)

    def positions(self, market=None):
        return self.exchange.interface.get_account_positions(market=market)

    def offers(self, market):
        return self.exchange.interface.get_account_positions(market=market)

    def lends(self, market):
        return self.exchange.interface.get_account_lends(market=market)

    def wallets(self, label=None):
        response = self.exchange.interface.get_account_wallets()
        result = Wallets()
        for kw, entries in response.items():
            wallet = ExchangeWallet(
                account=self,
                label=kw,
                balances=Balances()
            )
            for entry in entries:
                instrument_code = entry['instrument']['code']
                instrument = self.exchange.instruments[instrument_code]
                balance = Balance(
                    amount=entry['amount'],
                    available=entry['available'],
                    instrument=instrument,
                    wallet=wallet,
                )
                wallet.balances.append(balance)
            result.append(wallet)

        if label is None:
            return result
        else:
            return result[label]

    def deposits(self):
        return self.exchange.interface.get_account_deposits()

    def withdrawals(self):
        return self.exchange.interface.get_account_withdrawals()

    def create_order(self, *args, **kwargs):
        kwargs['account'] = self
        kwargs['exchange'] = self.exchange
        return Order(*args, **kwargs)

    def create_offer(self, *args, **kwargs):
        kwargs['account'] = self
        kwargs['exchange'] = self.exchange
        return Offer(*args, **kwargs)

    def create_deposit_address(self):
        raise NotImplementedError

    def create_withdraw(self):
        raise NotImplementedError

    def create_transfer(self):
        raise NotImplementedError

    def place(self, obj):
        if type(obj) is Order:
            self.exchange.interface.place_single_order(obj)
        elif type(obj) is Orders:
            self.exchange.interface.place_multiple_orders(obj)
        elif type(obj) is Offer:
            self.exchange.interface.place_single_offer(obj)
        elif type(obj) is Offers:
            self.exchange.interface.place_multiple_offers(obj)
        return obj

    def update(self, obj):
        if type(obj) is Order:
            self.exchange.interface.update_single_order(obj)
        elif type(obj) is Orders:
            self.exchange.interface.update_multiple_orders(obj)
        elif type(obj) is Offer:
            self.exchange.interface.update_single_offer(obj)
        elif type(obj) is Offers:
            self.exchange.interface.update_multiple_offers(obj)
        return obj

    def cancel(self, obj):
        if type(obj) is Order:
            self.exchange.interface.cancel_single_order(obj)
        elif type(obj) is Orders:
            self.exchange.interface.cancel_multiple_orders(obj)
        elif type(obj) is Offer:
            self.exchange.interface.cancel_single_offer(obj)
        elif type(obj) is Offers:
            self.exchange.interface.cancel_multiple_offers(obj)
        return obj

    def replace(self, obj):
        if type(obj) is Order:
            self.exchange.interface.replace_single_order(obj)
        elif type(obj) is Orders:
            self.exchange.interface.replace_multiple_orders(obj)
        elif type(obj) is Offer:
            self.exchange.interface.replace_single_offer(obj)
        elif type(obj) is Offers:
            self.exchange.interface.replace_multiple_offers(obj)
        return obj


class Accounts(ObjectList):

    @staticmethod
    def from_keystore(keystore, exchanges):
        accounts = Accounts()
        for exchange_slug in keystore.groups():
            exchange_slug = str(exchange_slug)
            if exchange_slug in exchanges.slugs:
                for label in keystore[exchange_slug].keys():
                    credentials = Credentials(key=keystore[exchange_slug][label]['key'],
                                              secret=keystore[exchange_slug][label]['secret'])
                    account = Account(exchange=exchanges[exchange_slug], credentials=credentials,
                                      label=label)
                    accounts.append(account)
        return accounts

    def __getattr__(self, item):
        for account in self:
            exchange_slug = account.exchange.interface.slug
            credentials_label = account.label
            key = '{}_{}'.format(exchange_slug, credentials_label)
            if key == item:
                return account
        raise AttributeError("'{}' object contains no item: '{}'".format(self.__class__.__name__, item))

    def __getitem__(self, item):
        if type(item) is str:
            for account in self:
                exchange_slug = account.exchange.interface.slug
                credentials_label = account.label
                key = '{}_{}'.format(exchange_slug, credentials_label)
                if key == item:
                    return account
            raise KeyError("'{}' object contains no item: '{}'".format(self.__class__.__name__, item))
        else:
            return super(self.__class__, self).__getitem__(item)

    def as_dict(self):
        result = dict()
        for account in self:
            exchange_slug = account.exchange.interface.slug
            credentials_label = account.label
            account_key = '{}_{}'.format(exchange_slug, credentials_label)
            result.update({account_key: account})
        return result

    @property
    def slugs(self):
        result = list()
        for account in self:
            exchange_slug = account.exchange.interface.slug
            credentials_label = account.label
            key = '{}_{}'.format(exchange_slug, credentials_label)
            result.append(key)
        return result
