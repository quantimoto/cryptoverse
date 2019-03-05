class ExchangeInterface(object):
    # Methods names in this class should be very explicit and clear. The methods should do one thing quick and simple.
    rest_client = None
    scrape_client = None
    slug = None

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}()'.format(class_name)

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.rest_client, self.scrape_client, self.slug) == (
                    other.rest_client, other.scrape_client, other.slug):
                return True
        return False

    def __hash__(self):
        return hash((self.rest_client, self.scrape_client, self.slug))

    def copy(self):
        obj = self.__class__()
        return obj

    def get_spot_instruments(self):
        raise NotImplementedError

    def get_margin_instruments(self):
        raise NotImplementedError

    def get_funding_instruments(self):
        raise NotImplementedError

    def get_all_instruments(self):
        raise NotImplementedError

    def get_spot_pairs(self):
        raise NotImplementedError

    def get_margin_pairs(self):
        raise NotImplementedError

    def get_all_pairs(self):
        raise NotImplementedError

    def get_spot_markets(self):
        raise NotImplementedError

    def get_margin_markets(self):
        raise NotImplementedError

    def get_funding_markets(self):
        raise NotImplementedError

    def get_all_markets(self):
        raise NotImplementedError

    def get_fees(self):
        raise NotImplementedError

    def get_ticker(self, symbol):
        raise NotImplementedError

    def get_tickers(self, symbols):
        raise NotImplementedError

    def get_all_tickers(self):
        raise NotImplementedError

    def get_market_orders(self, pair, limit=100):
        raise NotImplementedError

    def get_market_trades(self, pair, limit=100):
        raise NotImplementedError

    def get_market_offers(self, instrument, limit=100):
        raise NotImplementedError

    def get_market_lends(self, instrument, limit=100):
        raise NotImplementedError

    def get_market_candles(self, period, pair, limit=100):
        raise NotImplementedError

    def get_account_fees(self, credentials=None):
        raise NotImplementedError

    def get_account_wallets(self, credentials=None):
        raise NotImplementedError

    def get_account_active_orders(self, credentials=None):
        raise NotImplementedError

    def get_account_order_history(self, credentials=None):
        raise NotImplementedError

    def get_account_trades(self, pair, limit, credentials=None):
        raise NotImplementedError

    def get_account_trades_for_order(self, order_id, pair, credentials=None):
        raise NotImplementedError

    def get_account_positions(self, credentials=None):
        raise NotImplementedError

    def get_account_offers(self, credentials=None):
        raise NotImplementedError

    def get_account_active_lends(self, instrument, limit=100, credentials=None):
        raise NotImplementedError

    def get_account_lending_history(self, begin=None, end=None, limit=100):
        raise NotImplementedError

    def get_account_lends_for_offer(self, instrument, offer_id, credentials=None):
        raise NotImplementedError

    def get_account_deposits(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def get_account_withdrawals(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def place_single_order(self, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                           post_only=None, credentials=None):
        raise NotImplementedError

    def place_multiple_orders(self, orders, credentials=None):
        raise NotImplementedError

    def replace_single_order(self, order_id, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                             post_only=None, credentials=None):
        raise NotImplementedError

    def replace_multiple_orders(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def update_single_order(self, order_id, credentials=None):
        raise NotImplementedError

    def update_multiple_orders(self, order_ids, credentials=None):
        raise NotImplementedError

    def cancel_single_order(self, order_id, credentials=None):
        raise NotImplementedError

    def cancel_multiple_orders(self, order_ids, credentials=None):
        raise NotImplementedError

    def cancel_all_orders(self, credentials=None):
        raise NotImplementedError

    def place_single_offer(self, instrument, amount, daily_rate, duration, side, credentials=None):
        raise NotImplementedError

    def place_multiple_offers(self, offers, credentials=None):
        raise NotImplementedError

    def replace_single_offer(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def replace_multiple_offers(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def update_single_offer(self, offer_id, credentials=None):
        raise NotImplementedError

    def update_multiple_offers(self, offer_ids, credentials=None):
        raise NotImplementedError

    def cancel_single_offer(self, offer_id, credentials=None):
        raise NotImplementedError

    def cancel_multiple_offers(self, offer_ids, credentials=None):
        raise NotImplementedError

    def cancel_all_offers(self, credentials=None):
        raise NotImplementedError
