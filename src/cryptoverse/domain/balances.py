from .instruments import Instrument, Instruments
from .markets import Markets
from .object_list import ObjectList
from .orders import Order


class Balance(object):
    amount = None
    available = None
    _instrument = None
    wallet = None

    def __init__(self, instrument=None, amount=None, available=None, wallet=None):
        self.instrument = instrument
        self.amount = amount
        self.available = available
        self.wallet = wallet

    def __repr__(self):
        return '{}(instrument={instrument}, ' \
               'amount={amount:.8f}, ' \
               'available={available:.8f})'.format(self.__class__.__name__, **self.as_dict())

    def as_dict(self):
        dict_obj = dict()
        for key in ['instrument', 'amount', 'available']:
            value = getattr(self, key)
            if value is not None:
                dict_obj.update({key: value})
        return dict_obj

    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    def instrument(self, value):
        if value is not None:
            if type(value) is Instrument:
                self._instrument = value
            elif type(value) is dict:
                self._instrument = Instrument.from_dict(value)
            elif type(value) is str:
                self._instrument = Instrument.from_str(value)

    def markets(self, quote_instrument):
        if self.instrument == quote_instrument:
            result = Markets()
        else:
            exchange = self.wallet.account.exchange
            result = exchange.spot_markets.find(base=self.instrument, quote=quote_instrument)
            if not result:
                result = exchange.spot_markets.find(quote=self.instrument, base=quote_instrument)
            if not result:
                markets_with_instrument = exchange.spot_markets.with_instruments(self.instrument)
                intermediate_instrument_candidates = (markets_with_instrument.get_values('base') +
                                                      markets_with_instrument.get_values('quote')).get_unique()

                intermediate_market, final_market = None, None
                for intermediate_instrument in intermediate_instrument_candidates:
                    if intermediate_instrument != self.instrument and intermediate_instrument != quote_instrument and \
                            exchange.spot_markets[self.instrument, intermediate_instrument] and \
                            exchange.spot_markets[intermediate_instrument, quote_instrument]:
                        intermediate_market = exchange.spot_markets[self.instrument, intermediate_instrument]
                        final_market = exchange.spot_markets[intermediate_instrument, quote_instrument]
                        break
                if intermediate_market and final_market:
                    result = Markets()
                    result.append(intermediate_market)
                    result.append(final_market)
        return result

    def value_in(self, quote_instrument, tickers=None):
        if self.wallet is not None and self.wallet.account is not None:
            exchange = self.wallet.account.exchange
            account = self.wallet.account
            base_instrument = self.instrument
            amount = self.amount

            if tickers is None:
                markets = self.markets(quote_instrument=quote_instrument)
                tickers = exchange.tickers(markets)

            market = self.wallet.account.exchange.spot_markets[base_instrument, quote_instrument]
            if type(market) is Markets and len(market) > 0:
                market = market.first

            if not market:
                markets_with_instrument = exchange.spot_markets.with_instruments(base_instrument)
                intermediate_instrument_candidates = (markets_with_instrument.get_values('base') +
                                                      markets_with_instrument.get_values('quote')).get_unique()
                for intermediate_instrument in intermediate_instrument_candidates:
                    if intermediate_instrument != base_instrument and intermediate_instrument != quote_instrument and \
                            exchange.spot_markets[base_instrument, intermediate_instrument] and \
                            exchange.spot_markets[intermediate_instrument, quote_instrument]:
                        amount = self.value_in(intermediate_instrument, tickers=tickers)
                        market = exchange.spot_markets[intermediate_instrument, quote_instrument]
                        break

            if market:
                side = market.get_side(output_instrument=quote_instrument)
                if tickers is not None:
                    ticker = tickers.get(market=market)
                    price = ticker.bid if side == 'buy' else ticker.ask
                else:
                    price = 'bid' if side == 'buy' else 'ask'
                result = Order(
                    account=account,
                    market=market,
                    side=side,
                    input=amount,
                    price=price,
                ).output
                return result
            else:
                raise ValueError(
                    "No market found for supplied instrument: {}/{}".format(base_instrument.code, quote_instrument))


class Balances(ObjectList):

    def get_by_instrument(self, *instruments):
        result = self.__class__()
        for instrument in instruments:
            result = result + self.find(instrument=instrument)
        return result

    def values_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.markets(quote_instrument=quote_instrument)
            from .tickers import Tickers
            tickers = Tickers()
            for exchange in markets.get_unique_values('exchange'):
                exchange_markets = markets.find(exchange=exchange)
                tickers += exchange.tickers(exchange_markets)

        values = dict()  # todo: this overwrites data when calculating values for multiple accounts
        for entry in self:
            if entry.instrument.code not in values and entry.amount != 0:
                values[entry.instrument.code] = 0
            if entry.instrument != quote_instrument:
                values[entry.instrument.code] += entry.value_in(quote_instrument=quote_instrument, tickers=tickers)
            else:
                values[entry.instrument.code] += entry.amount

        return values

    def value_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.markets(quote_instrument=quote_instrument)
            from .tickers import Tickers
            tickers = Tickers()
            for exchange in markets.get_unique_values('exchange'):
                exchange_markets = markets.find(exchange=exchange)
                tickers += exchange.tickers(exchange_markets)

        instrument_values = self.values_in(quote_instrument=quote_instrument, tickers=tickers)
        return sum(instrument_values.values())

    def weights(self, quote_instrument='BTC', tickers=None):
        instrument_values = self.values_in(quote_instrument=quote_instrument, tickers=tickers)
        total_value = sum(instrument_values.values())
        weights = dict()
        for instrument_code, value in instrument_values.items():
            weights.update({
                instrument_code: value / total_value
            })
        return weights

    @property
    def instruments(self):
        return Instruments(self.get_unique_values('instrument'))

    def markets(self, quote_instrument):
        result = Markets()
        for entry in self:
            result += entry.markets(quote_instrument=quote_instrument)
        return result.get_unique()

    def collapse(self):
        result = type(self)()
        for instrument in self.instruments:
            balance = Balance(
                instrument=instrument,
                amount=self.find(instrument=instrument).get_sum('amount'),
                available=self.find(instrument=instrument).get_sum('available'),
            )
            result.append(balance)
        return result
