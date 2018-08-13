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

    def get_spot_instruments(self):
        raise NotImplementedError

    def get_margin_instruments(self):
        raise NotImplementedError

    def get_funding_instruments(self):
        raise NotImplementedError

    def get_spot_markets(self, *args, **kwargs):
        raise NotImplementedError

    def get_margin_markets(self, *args, **kwargs):
        raise NotImplementedError

    def get_funding_markets(self, *args, **kwargs):
        raise NotImplementedError

    def get_fee_information(self, *args, **kwargs):
        raise NotImplementedError

    def get_ticker(self, *args, **kwargs):
        raise NotImplementedError

    def get_market_orders(self, *args, **kwargs):
        raise NotImplementedError

    def get_market_trades(self, *args, **kwargs):
        raise NotImplementedError

    def get_market_offers(self, *args, **kwargs):
        raise NotImplementedError

    def get_market_lends(self, *args, **kwargs):
        raise NotImplementedError

    def get_market_candles(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_orders(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_trades(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_offers(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_lends(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_balances(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_deposits(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_withdraws(self, *args, **kwargs):
        raise NotImplementedError

    def place_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def place_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def replace_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def replace_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def update_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def update_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_orders(self, *args, **kwargs):
        raise NotImplementedError

    def place_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def place_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def replace_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def replace_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def update_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def update_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_offers(self, *args, **kwargs):
        raise NotImplementedError
