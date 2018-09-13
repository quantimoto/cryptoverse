from memoized_property import memoized_property

from .instruments import Instrument, Instruments
from .lends import Lend, Lends
from .markets import Market, Markets
from .object_list import ObjectList
from .offers import Offer, Offers, OfferBook
from .orders import Order, Orders, OrderBook
from .pairs import Pair, Pairs
from .tickers import Ticker, Tickers
from .trades import Trades, Trade


class Exchange(object):
    # High level exchange access. Simple friendly methods with smart responses
    interface = None

    def __init__(self, interface=None):
        self.set_interface(interface)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        kwarg_strings = list()
        for kw in []:
            kwarg_strings.append('{0}={1!r}'.format(kw, self.__dict__[kw]))
        return '{}({})'.format(class_name, ', '.join(kwarg_strings))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if self.interface == other.interface:
                return True
        return False

    def __hash__(self):
        return hash(self.interface)

    def set_interface(self, value=None):
        if value is not None:
            self.interface = value

    def copy(self):
        interface = self.interface.copy()
        obj = self.__class__(interface=interface)
        return obj

    @property
    def rest_client(self):
        if self.interface:
            return self.interface.rest_client

    @property
    def scrape_client(self):
        if self.interface:
            return self.interface.scrape_client

    @memoized_property
    def instruments(self):
        response = self.interface.get_all_instruments()
        result = Instruments()
        for entry in response:
            obj = Instrument.from_dict(entry)
            result.append(obj)
        return result

    @memoized_property
    def pairs(self):
        response = self.interface.get_all_pairs()
        result = Pairs()
        for entry in response:
            obj = Pair.from_dict(entry)
            result.append(obj)
        return result

    @memoized_property
    def markets(self):
        response = self.interface.get_all_markets()
        result = Markets()
        for k, v in response.items():
            for entry in v:
                entry['exchange'] = self
                obj = Market.from_dict(entry)
                result.append(obj)
        return result

    @memoized_property
    def spot_markets(self):
        response = self.interface.get_spot_markets()
        result = Markets()
        for entry in response:
            entry['exchange'] = self
            obj = Market.from_dict(entry)
            result.append(obj)
        return result

    @memoized_property
    def margin_markets(self):
        response = self.interface.get_margin_markets()
        result = Markets()
        for entry in response:
            entry['exchange'] = self
            obj = Market.from_dict(entry)
            result.append(obj)
        return result

    @memoized_property
    def funding_markets(self):
        response = self.interface.get_funding_markets()
        result = Markets()
        for entry in response:
            entry['exchange'] = self
            obj = Market.from_dict(entry)
            result.append(obj)
        return result

    def fees(self):
        return self.interface.get_fees()

    def ticker(self, market):
        if type(market) is Market:
            symbol = market.pair.as_str()
        elif type(market) is Pair:
            symbol = market.as_str()
        elif type(market) is str and Pair.is_valid_str(market):
            symbol = Pair.from_str(market).as_str()
        else:
            symbol = None

        if symbol is not None:
            response = self.interface.get_ticker(symbol=symbol)
            result = Ticker.from_dict(response)
            return result

    def tickers(self, *markets):
        symbols = list()
        if len(markets) == 1 and type(markets[0]) is list:
            markets = markets[0]
        elif len(markets) == 1 and type(markets[0]) in [Markets, Pairs]:
            markets = markets[0]

        for entry in markets:
            if type(entry) is str and '/' in entry:
                symbol = entry
            elif type(entry) is Pair:
                symbol = entry.as_str()
            elif type(entry) is Market:
                symbol = entry.symbol.as_str()
            else:
                symbol = None

            if symbol is not None:
                symbols.append(symbol)

        response = self.interface.get_tickers(*symbols)
        result = Tickers()
        for entry in response:
            if 'base' in entry['market'] and 'quote' in entry['market']:
                market = self.markets[entry['market']['base']['code'], entry['market']['quote']['code']]
                if type(market) is Markets:
                    market = market.first
            elif 'code' in entry['market']:
                market = self.markets[entry['market']['code']]
            else:
                market = None

            if market is not None:
                entry.update({'market': market})
                obj = Ticker.from_dict(entry)
                result.append(obj)

        return result

    def order_book(self, market, limit=100):
        if type(market) is Market:
            pair_str = market.pair.as_str()
            pair_obj = market.pair
        elif type(market) is Pair:
            pair_str = market.as_str()
            pair_obj = market
        elif type(market) is str and '/' in market:
            pair_str = market
            pair_obj = market
        else:
            pair_str = None
            pair_obj = None

        if pair_str is not None:
            response = self.interface.get_market_orders(pair=pair_str, limit=limit)

            bids = Orders()
            if 'bids' in response:
                for entry in response['bids']:
                    entry['exchange'] = self
                    entry['pair'] = pair_obj
                    order = Order.from_dict(entry)
                    bids.append(order)

            asks = Orders()
            if 'asks' in response:
                for entry in response['asks']:
                    entry['exchange'] = self
                    entry['pair'] = pair_obj
                    order = Order.from_dict(entry)
                    asks.append(order)

            result = OrderBook(bids, asks)

            return result

    def offer_book(self, market, limit=100):
        if type(market) is Market:
            instrument_str = market.instrument.as_str()
            instrument_obj = market.instrument
        elif type(market) is Instrument:
            instrument_str = market.as_str()
            instrument_obj = market
        elif type(market) is str:
            instrument_str = market
            instrument_obj = market
        else:
            instrument_str = None
            instrument_obj = None

        if instrument_str is not None:
            response = self.interface.get_market_offers(instrument=instrument_str, limit=limit)

            bids = Offers()
            if 'bids' in response:
                for entry in response['bids']:
                    entry['exchange'] = self
                    entry['instrument'] = instrument_obj
                    offer = Offer.from_dict(entry)
                    bids.append(offer)

            asks = Offers()
            if 'asks' in response:
                for entry in response['asks']:
                    entry['exchange'] = self
                    entry['instrument'] = instrument_obj
                    offer = Offer.from_dict(entry)
                    asks.append(offer)

            result = OfferBook(bids, asks)

            return result

    def trades(self, market, limit=100):
        if type(market) is Market:
            pair_str = market.pair.as_str()
            pair_obj = market.pair
        elif type(market) is Pair:
            pair_str = market.as_str()
            pair_obj = market
        elif type(market) is str and '/' in market:
            pair_str = market
            pair_obj = market
        else:
            pair_str = None
            pair_obj = None

        if pair_str is not None:
            response = self.interface.get_market_trades(pair=pair_str, limit=limit)
            result = Trades()
            for entry in response:
                entry['exchange'] = self
                entry['pair'] = pair_obj
                trade = Trade.from_dict(entry)
                result.append(trade)
            return result

    def lends(self, market, limit=100):
        if type(market) is Market:
            instrument_str = market.instrument.as_str()
            instrument_obj = market.instrument
        elif type(market) is Instrument:
            instrument_str = market.as_str()
            instrument_obj = market
        elif type(market) is str:
            instrument_str = market
            instrument_obj = market
        else:
            instrument_str = None
            instrument_obj = None

        if instrument_str is not None:
            response = self.interface.get_market_lends(instrument=instrument_str, limit=limit)
            result = Lends()
            for entry in response:
                entry['exchange'] = self
                entry['instrument'] = instrument_obj
                lend = Lend.from_dict(entry)
                result.append(lend)
            return result

    def create_order(self, *args, **kwargs):
        kwargs['exchange'] = self
        from ..domain import Order
        order = Order(*args, **kwargs)
        return order

    def create_offer(self, *args, **kwargs):
        kwargs['exchange'] = self
        from ..domain import Offer
        offer = Offer(*args, **kwargs)
        return offer


class Exchanges(ObjectList):

    def __getattr__(self, item):
        for exchange in self:
            if str(exchange.interface.slug).lower() == str(item).lower():
                return exchange
        raise AttributeError("'{}' object has no attribute: '{}'".format(self.__class__.__name__, item))

    def __getitem__(self, item):
        for exchange in self:
            if str(exchange.interface.slug).lower() == str(item).lower():
                return exchange
        raise KeyError("'{}' object has no item: '{}'".format(self.__class__.__name__, item))

    @property
    def slugs(self):
        result = list()
        for exchange in self:
            result.append(exchange.interface.slug)
        return result

    def as_dict(self):
        result = dict()
        for exchange in self:
            result.update({
                exchange.interface.slug: exchange
            })
        return result
