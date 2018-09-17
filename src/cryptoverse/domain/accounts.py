from .balances import Balance, Balances
from .credentials import Credentials
from .lends import Lends, Lend
from .markets import Market
from .object_list import ObjectList
from .offers import Offer, Offers
from .orders import Order, Orders
from .pairs import Pair
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

    def orders(self):
        from .trades import Trades
        response = self.exchange.interface.get_account_orders()

        result = Orders()
        for entry in response:
            entry['account'] = self
            entry['exchange'] = self.exchange
            order = Order.from_dict(entry)
            result.append(order)

        markets = result.get_unique_values('market')
        trades = Trades()
        for market in markets:
            response = self.trades(market=market, limit=100)
            trades += response

        for entry in result:
            entry.trades = trades.find(order_id=entry.id)

        return result

    def trades(self, market, limit=100):
        from .markets import Market
        from .pairs import Pair
        from .trades import Trades, Trade

        if type(market) is Market:
            pair_str = market.pair.as_str()
            pair_obj = market.pair
        elif type(market) is Pair:
            pair_str = market.as_str()
            pair_obj = market
        elif type(str) and '/' in market:
            pair_str = market
            pair_obj = market
        else:
            raise ValueError("Invalid value for 'market' supplied: {}".format(market))

        response = self.exchange.interface.get_account_trades(pair=pair_str, limit=limit)

        result = Trades()
        for entry in response:
            entry['account'] = self
            entry['exchange'] = self.exchange
            entry['pair'] = pair_obj
            trade = Trade.from_dict(entry)
            result.append(trade)

        return result

    def positions(self, market=None):
        return self.exchange.interface.get_account_positions(market=market)

    def offers(self):
        response = self.exchange.interface.get_account_offers()

        result = Offers()
        for entry in response:
            entry['account'] = self
            entry['exchange'] = self.exchange
            order = Offer.from_dict(entry)
            result.append(order)

        markets = result.get_unique_values('market')
        lends = Lends()
        for market in markets:
            response = self.lends(market=market, limit=100)
            lends += response

        for entry in result:
            entry.lends = lends.find(offer_id=entry.id)

        return result

    def lends(self, market, limit=100):

        if type(market) is Market:
            instrument_str = market.instrument.as_str()
            instrument_obj = market.instrument
        elif type(market) is Pair:
            instrument_str = market.as_str()
            instrument_obj = market
        elif type(str):
            instrument_str = market
            instrument_obj = market
        else:
            raise ValueError("Invalid value for 'market' supplied: {}".format(market))

        response = self.exchange.interface.get_account_lends(instrument=instrument_str, limit=limit)

        result = Lends()
        for entry in response:
            entry['account'] = self
            entry['exchange'] = self.exchange
            entry['instrument'] = instrument_obj
            trade = Lend.from_dict(entry)
            result.append(trade)

        return result

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
            response = self.exchange.interface.place_single_order(
                pair=obj.pair.as_str(),
                amount=obj.amount,
                price=obj.price,
                side=obj.side,
                context=obj.context,
                type_=obj.type,
                hidden=obj.hidden,
            )
            obj.update_arguments(**response)

        elif type(obj) is Orders:
            response = self.exchange.interface.place_multiple_orders(obj)
            return response

        elif type(obj) is Offer:
            response = self.exchange.interface.place_single_offer(
                instrument=obj.instrument.as_str(),
                amount=obj.amount,
                annual_rate=obj.annual_rate,
                period=obj.period,
                side=obj.side,
            )
            obj.update_arguments(**response)

        elif type(obj) is Offers:
            response = self.exchange.interface.place_multiple_offers(obj)
            return response

        return obj

    def update(self, obj):

        if type(obj) is Order:
            response = self.exchange.interface.update_single_order(order_id=obj.id)
            obj.update_arguments(**response)

            trades = self.trades(market=obj.market, limit=100)
            obj.trades = trades.find(order_id=obj.id)

        elif type(obj) is Orders:
            response = self.exchange.interface.update_multiple_orders(obj.get_values('id'))
            return response

        elif type(obj) is Offer:
            response = self.exchange.interface.update_single_offer(obj.id)
            obj.update_arguments(**response)

            lends = self.lends(market=obj.market, limit=100)
            obj.lends = lends.find(offer_id=obj.id)

        elif type(obj) is Offers:
            response = self.exchange.interface.update_multiple_offers(obj.get_values('id'))
            return response

        return obj

    def cancel(self, obj):

        if type(obj) is Order:
            response = self.exchange.interface.cancel_single_order(obj.id)
            obj.update_arguments(**response)
            if not obj.is_cancelled:
                while not obj.is_cancelled:
                    obj = self.update(obj)

        elif type(obj) is Orders:
            response = self.exchange.interface.cancel_multiple_orders(obj.get_values('id'))
            return response

        elif type(obj) is Offer:
            response = self.exchange.interface.cancel_single_offer(obj.id)
            obj.update_arguments(**response)
            if not obj.is_cancelled:
                while not obj.is_cancelled:
                    obj = self.update(obj)

        elif type(obj) is Offers:
            response = self.exchange.interface.cancel_multiple_offers(obj.get_values('id'))
            return response

        return obj

    def replace(self, old_obj, new_obj):

        if type(old_obj) is Order and type(new_obj) is Order:
            response = self.exchange_auth.interface.replace_single_order(
                order_id=old_obj.id,
                pair=new_obj.pair.as_str(),
                amount=new_obj.amount,
                price=new_obj.price,
                side=new_obj.side,
                context=new_obj.context,
                type_=new_obj.type,
                hidden=new_obj.hidden,
            )
            new_obj.update_arguments(**response)
            old_obj.update()

        # elif type(old_obj) is Orders and type(new_obj) is Orders:
        #     response = self.exchange_auth.interface.replace_multiple_orders(obj.get_values('id'))
        #     return response
        #
        # elif type(old_obj) is Offer and type(new_obj) is Offer:
        #     response = self.exchange_auth.interface.replace_single_offer(obj.id)
        #     return response
        #
        # elif type(old_obj) is Offers and type(new_obj) is Offers:
        #     response = self.exchange_auth.interface.replace_multiple_offers(obj.get_values('id'))
        #     return response

        return Orders([old_obj, new_obj])


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

    @property
    def slugs(self):
        result = list()
        for account in self:
            exchange_slug = account.exchange.interface.slug
            credentials_label = account.label
            key = '{}_{}'.format(exchange_slug, credentials_label)
            result.append(key)
        return result

    def as_dict(self):
        result = dict()
        for account in self:
            exchange_slug = account.exchange.interface.slug
            credentials_label = account.label
            account_key = '{}_{}'.format(exchange_slug, credentials_label)
            result.update({account_key: account})
        return result
