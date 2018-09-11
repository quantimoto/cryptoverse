from unittest import TestCase

from cryptoverse.base.rest.response import ResponseObj
from cryptoverse.exchanges.rest import BitfinexREST

bitfinex = BitfinexREST()


class TestBitfinexREST(TestCase):

    def test_pubticker(self):
        response = bitfinex.pubticker(symbol='btcusd')
        self.assertIsInstance(response, ResponseObj)

    def test_stats(self):
        response = bitfinex.stats(symbol='btcusd')
        self.assertIsInstance(response, ResponseObj)

    def test_lendbook(self):
        response = bitfinex.lendbook(currency='usd')
        print(response)
        self.assertIsInstance(response, ResponseObj)

    def test_book(self):
        response = bitfinex.book(symbol='btcusd')
        self.assertIsInstance(response, ResponseObj)

    def test_trades(self):
        response = bitfinex.trades(symbol='btcusd')
        self.assertIsInstance(response, ResponseObj)

    def test_lends(self):
        response = bitfinex.lends(currency='usd')
        self.assertIsInstance(response, ResponseObj)

    def test_symbols(self):
        response = bitfinex.symbols()
        self.assertIsInstance(response, ResponseObj)

    def test_symbol_details(self):
        response = bitfinex.symbols_details()
        self.assertIsInstance(response, ResponseObj)

    def test_tickers(self):
        response = bitfinex.tickers(symbols='tBTCUSD')
        self.assertIsInstance(response, ResponseObj)

    def test_ticker(self):
        response = bitfinex.ticker(symbol='tBTCUSD')
        self.assertIsInstance(response, ResponseObj)

    def test_trades_hist(self):
        response = bitfinex.trades_hist(symbol='tBTCUSD')
        self.assertIsInstance(response, ResponseObj)

    def test_book_v2(self):
        response = bitfinex.book_v2(symbol='tBTCUSD')
        self.assertIsInstance(response, ResponseObj)

    def test_stats1(self):
        response = bitfinex.stats1(key='funding.size', size='1m', symbol='fUSD', side='long', section='hist')
        self.assertIsInstance(response, ResponseObj)

    def test_candles(self):
        response = bitfinex.candles(timeframe='1h', symbol='tBTCUSD', section='hist')
        self.assertIsInstance(response, ResponseObj)

    def test_calc_market_average_price(self):
        response = bitfinex.calc_market_average_price(symbol='tBTCUSD', amount='10')
        self.assertIsInstance(response, ResponseObj)

    # def test_foreign_exchange_rate(self):
    #     response = bitfinex.foreign_exchange_rate(ccy1='BTC',
    #                                               ccy2='USD')  # todo: ask bitfinex support why this doesn't work
    #     self.assertIsInstance(response, ResponseObj)
