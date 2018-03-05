import requests

from ...base.rest import RESTClient, rate_limit


class Bl3pREST(RESTClient):
    base_url = 'https://api.bl3p.eu'
    public_endpoint = '/{version}/{market}/{command}'
    authenticated_endpoint = '/{version}/{market}/{command}'

    @rate_limit(600, 600)  # https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md#24---capacity
    def public_request(self, url, params=None, data=None, headers=None, timeout=None, method='GET'):
        pass

    @rate_limit(600, 600)  # https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md#24---capacity
    def authenticated_request(self, endpoint, params=None, method='POST'):
        pass

    def ticker(self, market='BTCEUR'):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#21---ticker
        url = '{url}/{version}/{market}/{callname}'.format(**{
            'url': self.base_url,
            'version': 1,
            'market': market,
            'callname': 'ticker',
        })
        params = {}
        response = requests.get(url=url, params=params)
        return response

    def orderbook(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#22---orderbook
        pass

    def trades(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#23---last-1000-trades
        pass

    def order_add(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#21---create-an-order
        pass

    def order_cancel(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#22---cancel-an-order
        pass

    def order_result(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#23---get-a-specific-order
        pass

    def depth_full(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#24---get-the-whole-orderbook
        pass

    def wallet_history(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#31---get-your-transaction-history
        pass

    def new_deposit_address(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#32---create-a-new-deposit-address
        pass

    def deposit_address(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#33---get-the-last-deposit-address
        pass

    def withdraw(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#34---create-a-withdrawal
        pass

    def info(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#35---get-account-info--balance
        pass

    def orders(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#36-get-active-orders
        pass

    def orders_history(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#37-get-order-history
        pass

    def trades_fetch(self):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#38---fetch-all-trades-on-bl3p
        pass
