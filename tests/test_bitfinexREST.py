from unittest import TestCase

import requests

from cryptoverse.exchanges.rest import BitfinexREST

bitfinex = BitfinexREST()


class TestBitfinexREST(TestCase):
    def test_pubticker(self):
        response = bitfinex.pubticker(symbol='btcusd')
        print(response)
        self.assertIsInstance(response, requests.models.Response)

    def test_stats(self):
        response = bitfinex.stats(symbol='btcusd')
        print(response)
        self.assertIsInstance(response, requests.models.Response)

    def test_lendbook(self):
        response = bitfinex.lendbook(currency='usd')
        print(response)
        self.assertIsInstance(response, requests.models.Response)

    def test_book(self):
        response = bitfinex.book(symbol='btcusd')
        self.assertIsInstance(response, requests.models.Response)

    # def test_trades(self):
    #     self.fail()
    #
    # def test_lends(self):
    #     self.fail()
    #
    # def test_symbols(self):
    #     self.fail()
    #
    # def test_symbol_details(self):
    #     self.fail()
    #
    # def test_tickers(self):
    #     self.fail()
    #
    # def test_ticker(self):
    #     self.fail()
    #
    # def test_trades_hist(self):
    #     self.fail()
    #
    # def test_book_v2(self):
    #     self.fail()
    #
    # def test_stats1(self):
    #     self.fail()
    #
    # def test_candles(self):
    #     self.fail()
    #
    # def test_calc_market_average_price(self):
    #     self.fail()
    #
    # def test_foreign_exchange_rate(self):
    #     self.fail()
