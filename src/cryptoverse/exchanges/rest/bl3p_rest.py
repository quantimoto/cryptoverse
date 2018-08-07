import base64
import hashlib
import hmac
from urllib.parse import urlencode

from ...base.rest import RESTClient
from ...exceptions import MissingCredentialsError


class Bl3pREST(RESTClient):
    # https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md
    """
    Complete implementation of the Bl3p REST-api as documented at:
    https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md

    Methods here are a direct translation from python to the exchange's available methods. Method names and parameters
    reflect those in the official documentation as much as possible. Response is kept in-tact and no additional logic is
    executed in this obj.
    """

    address = 'https://api.bl3p.eu'
    uri_template = '/{version}/{endpoint}'

    credentials = None

    # Authentication methods

    def sign(self, request_obj, credentials):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md#23-authentication-and-authorization
        """
        Signs the request object using the supplied credentials, according to Bl3p's requirements.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """

        payload = request_obj.get_data().copy()

        encoded_payload = urlencode(payload)
        message = '%s%c%s' % (request_obj.get_uri(), 0x00, encoded_payload)

        h = hmac.new(
            key=base64.b64decode(credentials['secret']),
            msg=message,
            digestmod=hashlib.sha512,
        )
        signature = h.digest()

        headers = {
            'Rest-Key': credentials['key'],
            'Rest-Sign': base64.b64encode(signature),
        }
        request_obj.set_headers(headers)

        return request_obj

    # @rate_limit(600, 600)  # https://github.com/BitonicNL/bl3p-api/blob/master/docs/base.md#24---capacity
    # def query(self, *args, **kwargs):
    #     super(self.__class__, self).query(*args, **kwargs)

    #
    # V1 Public Endpoints
    #

    def ticker(self, market):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#21---ticker
        """
        Ticker

        :param str market: Market that the call will be applied to.
        :return:
        """

        response = self.query(
            method='GET',
            endpoint='{market}/{callname}',
            path_params={
                'version': 1,
                'market': market,
                'callname': 'ticker'
            },
        )

        return response

    def orderbook(self, market):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#22---orderbook
        """
        Orderbook

        :param str market: Market that the call will be applied to.
        :return:
        """

        response = self.query(
            method='GET',
            endpoint='{market}/{callname}',
            path_params={
                'version': 1,
                'market': market,
                'callname': 'orderbook'
            },
        )

        return response

    def trades(self, market):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/public_api/http.md#23---last-1000-trades
        """
        Last 1000 trades

        :param str market: Market that the call will be applied to.
        :return:
        """

        response = self.query(
            method='GET',
            endpoint='{market}/{callname}',
            path_params={
                'version': 1,
                'market': market,
                'callname': 'trades'
            },
        )

        return response

    #
    # V1 Authenticated Endpoints
    #

    def order_add(self, market, type_, amount_int, price_int, amount_funds_int, fee_currency, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#21---create-an-order
        """
        Create an order

        :param str market: Market that the call will be applied to.
        :param str type_: 'bid', 'ask'
        :param int amount_int: Amount BTC, amount LTC (*1e8)
        :param int price_int: Limit price in EUR (*1e5)
        :param int amount_funds_int: Maximal EUR amount to spend (*1e5)
        :param str fee_currency: Currency the fee is accounted in. Can be: 'EUR' or 'BTC'
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'order',
                'subcallname': 'add',
            },
            data={
                'type': type_,
                'amount_int': amount_int,
                'price_int': price_int,
                'amount_funds_int': amount_funds_int,
                'fee_currency': fee_currency,
            },
            credentials=credentials,
        )

        return response

    def order_cancel(self, market, order_id, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#22---cancel-an-order
        """

        :param str market: Market that the call will be applied to.
        :param int order_id: The id of the order that you wish to cancel.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'order',
                'subcallname': 'cancel',
            },
            data={
                'order_id': order_id,
            },
            credentials=credentials,
        )

        return response

    def order_result(self, market, order_id, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#23---get-a-specific-order
        """
        Get a specific order

        :param str market: Market that the call will be applied to.
        :param int order_id: The id of the order that you wish to retrieve.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'order',
                'subcallname': 'result',
            },
            data={
                'order_id': order_id,
            },
            credentials=credentials,
        )

        return response

    def depth_full(self, market, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#24---get-the-whole-orderbook
        """
        Get the whole orderbook

        :param str market: Market that the call will be applied to.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'depth',
                'subcallname': 'full',
            },
            credentials=credentials,
        )

        return response

    def wallet_history(self, currency, page=1, date_from=None, date_to=None, type_=None, recs_per_page=50,
                       credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#31---get-your-transaction-history
        """
        Get your transaction history

        :param str currency: Currency of the wallet. (Can be: 'BTC', 'EUR').
        :param int page: Page number. (1 = most recent transactions). Optional, default is 1.
        :param timestamp date_from: Filter the result by a Unix-timestamp. Transactions before this date will not be
            returned. Optional, default is no filter.
        :param timestamp date_to: Filter the result by a Unix-timestamp. Transactions after this date will not be
            returned. Optional, default is no filter.
        :param str type_: Filter the result by type. (Can be: ‘trade’, ‘fee’, ‘deposit’, ‘withdraw’). Optional, default
            is no filter.
        :param int recs_per_page: Number of records per page. Optional, default is 50.
        :param credentials: dictionary containing authentication information like key and secret.
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': 'GENMKT',
                'namespace': 'money',
                'callname': 'wallet',
                'subcallname': 'history',
            },
            data={
                'currency': currency,
                'page': page,
                'date_from': date_from,
                'date_to': date_to,
                'type': type_,
                'recs_per_page': recs_per_page,
            },
            credentials=credentials,
        )

        return response

    def new_deposit_address(self, currency, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#32---create-a-new-deposit-address
        """
        Create a new deposit address

        :param currency: Currency (Can be: 'BTC')
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}',
            path_params={
                'version': 1,
                'market': 'GENMKT',
                'namespace': 'money',
                'callname': 'new_deposit_address',
            },
            data={
                'currency': currency,
            },
            credentials=credentials,
        )

        return response

    def deposit_address(self, currency, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#33---get-the-last-deposit-address
        """
        Get the last deposit address

        :param currency: currency (Can be: 'BTC')
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{call_name}',
            path_params={
                'version': 1,
                'market': 'GENMKT',
                'namespace': 'money',
                'callname': 'deposit_address',
            },
            data={
                'currency': currency,
            },
            credentials=credentials,
        )

        return response

    def withdraw(self, currency, amount_int, account_id=None, account_name=None, address=None, extra_fee=None,
                 credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#34---create-a-withdrawal
        """
        Create a withdrawal

        :param currency: Currency (Can be: 'BTC', 'EUR')
        :param int amount_int: Satoshis or 0,00001 EUR
        :param str account_id: IBAN account-id (that is available within the regarding BL3P account)
        :param str account_name: IBAN account-name (should match your account verification)
        :param str address: The address to withdraw to
        :param int extra_fee: This will send the withdrawal as priority, extra fee will be charged (see bl3p.eu). Use 1
            for extra fee, default is no extra fee.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': 'GENMKT',
                'namespace': 'money',
                'callname': 'withdraw',
            },
            data={
                'currency': currency,
                'account_id': account_id,
                'account_name': account_name,
                'address': address,
                'extra_fee': extra_fee,
                'amount_int': amount_int,
            },
            credentials=credentials,
        )

        return response

    def info(self, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#35---get-account-info--balance
        """
        Get account info & balance

        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}',
            path_params={
                'version': 1,
                'market': 'GENMKT',
                'namespace': 'money',
                'callname': 'info',
            },
            credentials=credentials,
        )

        return response

    def orders(self, market, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#36-get-active-orders
        """
        Get active orders

        :param str market: Market that the call will be applied to.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'orders',
            },
            credentials=credentials,
        )

        return response

    def orders_history(self, market, page=1, date_from=None, date_to=None, recs_per_page=100, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#37-get-order-history
        """
        Get order history

        :param str market: Market that the call will be applied to.
        :param int page: Page number. (1 = most recent transactions). Default is 1.
        :param timestamp date_from: Filter the result by a Unix-timestamp. Transactions before this date will not be
            returned. Optional, default is no filter.
        :param timestamp date_to: Filter the result by a Unix-timestamp. Transactions after this date will not be
            returned. Optional, default is no filter.
        :param int recs_per_page: Number of records per page. Optional, default is 100.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'orders',
                'subcallname': 'history',
            },
            data={
                'page': page,
                'date_from': date_from,
                'date_to': date_to,
                'recs_per_page': recs_per_page,
            },
            credentials=credentials,
        )

        return response

    def trades_fetch(self, market, trade_id, credentials=None):
        # https://github.com/BitonicNL/bl3p-api/blob/master/docs/authenticated_api/http.md#38---fetch-all-trades-on-bl3p
        """
        Fetch all trades on Bl3p

        :param str market: Market that the call will be applied to.
        :param int trade_id: Id of the trade after which you want to fetch the (next) 1000 trades. If not specified,
            this call will return the last 1000 trades.
        :param credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='{market}/{namespace}/{callname}/{subcallname}',
            path_params={
                'version': 1,
                'market': market,
                'namespace': 'money',
                'callname': 'trades',
                'subcallname': 'fetch',
            },
            data={
                'trade_id': trade_id,
            },
            credentials=credentials,
        )

        return response
