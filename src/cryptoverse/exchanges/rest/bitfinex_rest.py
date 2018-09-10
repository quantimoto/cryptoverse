import base64
import hashlib
import hmac
import json
from json.decoder import JSONDecodeError

from requests.exceptions import ReadTimeout, ConnectionError

from ...base.rest import RESTClient
from ...base.rest.decorators import RateLimit, Memoize, Retry, formatter
from ...exceptions import MissingCredentialsException, ExchangeDecodeException, ExchangeRateLimitException, \
    ExchangeException, ExchangeUnavailableException, ExchangeInvalidResponseException


class BitfinexREST(RESTClient):
    # https://docs.bitfinex.com/docs
    """
    Complete implementation of the Bitfinex REST-api as documented at:
    https://docs.bitfinex.com/docs

    Methods here are a direct translation from the exchange's available methods to python. Method names and parameters
    reflect those in the official documentation as much as PEP allows. Response is kept in-tact and no additional logic
    is executed.
    """

    host = 'api.bitfinex.com'

    credentials = None

    # Authentication methods

    def sign(self, request_obj, credentials):
        # https://docs.bitfinex.com/docs/rest-auth
        # https://docs.bitfinex.com/v2/docs/rest-auth
        """
        Signs the request object using the supplied credentials, according to Bitfinex's requirements.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """
        payload = request_obj.params
        payload.update({
            'nonce': self.nonce(),
            'request': '/{}'.format(request_obj.path),
        })

        encoded_payload = base64.standard_b64encode(json.dumps(payload).encode('utf-8'))
        message = encoded_payload

        h = hmac.new(
            key=credentials.secret.encode('utf-8'),
            msg=message,
            digestmod=hashlib.sha384,
        )
        signature = h.hexdigest()

        headers = {
            'X-BFX-APIKEY': credentials.key,
            'X-BFX-PAYLOAD': encoded_payload,
            'X-BFX-SIGNATURE': signature,
        }
        request_obj.headers = headers

        return request_obj

    @Retry(ReadTimeout, wait=60)
    @Retry(ConnectionError, wait=60)
    @Retry(ExchangeDecodeException, wait=10, max_tries=3)
    @Retry(ExchangeRateLimitException, wait=20)
    @formatter
    def request(self, *args, **kwargs):
        result = super(BitfinexREST, self).request(*args, **kwargs)

        try:
            result_from_json = json.loads(result.text)
        except JSONDecodeError:
            if result.text == '':
                raise ExchangeInvalidResponseException
            else:
                print(result.text)
                raise ExchangeDecodeException

        if type(result_from_json) is dict and 'error' in result_from_json:
            if result_from_json['error'] == 'ERR_RATE_LIMIT':
                raise ExchangeRateLimitException
            elif result_from_json['code'] == 503 and result_from_json['error'] == 'temporarily_unavailable':
                raise ExchangeUnavailableException(result_from_json['error_description'])
            else:
                raise ExchangeException(result.json())
        elif type(result_from_json) is list and 'error' in result_from_json:
            raise ExchangeException(result.json())

        return result

    #
    # V1 Public Endpoints
    #

    @Memoize(expires=60. / 20)
    @RateLimit(calls=20, period=60)  # Documentation states: 20 req/min
    def pubticker(self, symbol):
        # https://docs.bitfinex.com/v1/reference#rest-public-ticker
        """
        Ticker

        The ticker is a high level overview of the state of the market. It shows you the current best bid and ask, as
        well as the last trade price. It also includes information such as daily volume and how much the price has moved
        over the last day.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        """

        response = self.request(
            method='GET',
            path='v{version}/pubticker/{symbol}',
            path_params={
                'version': 1,
                'symbol': symbol,
            },
        )

        return response

    @Memoize(expires=60. / 10)
    @RateLimit(calls=10, period=60)  # Documentation states: 10 req/min
    def stats(self, symbol):
        # https://docs.bitfinex.com/v1/reference#rest-public-stats
        """
        Stats

        Various statistics about the requested pair.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        """

        response = self.request(
            method='GET',
            path='v{version}/stats/{symbol}',
            path_params={
                'version': 1,
                'symbol': symbol,
            },
        )

        return response

    @Memoize(expires=60. / 10)
    @RateLimit(calls=10, period=60)  # Documentation states: 10 req/min
    def lendbook(self, currency, limit_bids=50, limit_asks=50):
        # https://docs.bitfinex.com/v1/reference#rest-public-fundingbook
        """
        Fundingbook

        Get the full margin funding book

        :param str currency:
        :param int limit_bids: Limit the number of funding bids returned. May be 0 in which case the array of bids is
            empty
        :param int limit_asks: Limit the number of funding offers returned. May be 0 in which case the array of asks is
            empty
        """

        response = self.request(
            method='GET',
            path='v{version}/lendbook/{currency}',
            path_params={
                'version': 1,
                'currency': currency,
            },
            query_params={
                'limit_bids': limit_bids,
                'limit_asks': limit_asks,
            },
        )

        return response

    @Memoize(expires=60. / 30)
    @RateLimit(calls=30, period=60)  # Documentation states: 60 req/min
    def book(self, symbol, limit_bids=50, limit_asks=50, group=1):
        # https://docs.bitfinex.com/v1/reference#rest-public-orderbook
        """
        Orderbook

        Get the full order book.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        :param int limit_bids: Limit the number of bids returned. May be 0 in which case the array of bids is empty
        :param int limit_asks: Limit the number of asks returned. May be 0 in which case the array of asks is empty
        :param int group: If 1, orders are grouped by price in the orderbook. If 0, orders are not grouped and sorted
            individually
        """
        response = self.request(
            method='GET',
            path='v{version}/book/{symbol}',
            path_params={
                'version': 1,
                'symbol': symbol,
            },
            query_params={
                'limit_bids': limit_bids,
                'limit_asks': limit_asks,
                'group': group,
            },
        )

        return response

    @Memoize(expires=60. / 20)
    @RateLimit(calls=20, period=60)  # Documentation states: 20 req/min
    def trades(self, symbol, timestamp=None, limit_trades=50):
        # https://docs.bitfinex.com/v1/reference#rest-public-trades
        """
        Trades

        Get a list of the most recent trades for the given symbol.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        :param timestamp: Only show trades at or after this timestamp
        :param int limit_trades: Limit the number of trades returned. Must be >= 1
        """
        response = self.request(
            method='GET',
            path='v{version}/trades/{symbol}',
            path_params={
                'version': 1,
                'symbol': symbol,
            },
            query_params={
                'timestamp': timestamp,
                'limit_trades': limit_trades,
            },
        )
        return response

    @Memoize(expires=60. / 30)
    @RateLimit(calls=30, period=60)  # Documentation states: 30 req/min
    def lends(self, currency, timestamp=None, limit_lends=50):
        # https://docs.bitfinex.com/v1/reference#rest-public-lends
        """
        Lends

        Get a list of the most recent funding data for the given currency: total amount provided and Flash Return Rate
        (in % by 365 days) over time.

        :param str currency:
        :param timestamp: Only show data at or after this timestamp
        :param int limit_lends: Limit the amount of funding data returned. Must be >= 1
        """

        response = self.request(
            method='GET',
            path='v{version}/lends/{currency}',
            path_params={
                'version': 1,
                'currency': currency,
            },
            query_params={
                'timestamp': timestamp,
                'limit_lends': limit_lends,
            },
        )

        return response

    @Memoize(expires=60. / 5)
    @RateLimit(calls=5, period=60)  # Documentation states: 5 req/min
    def symbols(self):
        # https://docs.bitfinex.com/v1/reference#rest-public-symbols
        """
        Symbols

        A list of symbol names.
        """

        response = self.request(
            method='GET',
            path='v{version}/symbols',
            path_params={
                'version': 1,
            },
        )

        return response

    @Memoize(expires=60. / 5)
    @RateLimit(calls=5, period=60)  # Documentation states: 5 req/min
    def symbols_details(self):
        # https://docs.bitfinex.com/v1/reference#rest-public-symbol-details
        """
        Symbol Details

        Get a list of valid symbol IDs and the pair details.
        """

        response = self.request(
            method='GET',
            path='v{version}/symbols_details',
            path_params={
                'version': 1,
            },
        )

        return response

    #
    # V1 Authenticated Endpoints
    #

    @Memoize(expires=60. / 1)
    @RateLimit(calls=1, period=60)
    def account_infos(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-account-info
        """
        Account Info

        Return information about your account (trading fees)

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/account_infos',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 1)
    @RateLimit(calls=1, period=60)
    def account_fees(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-fees
        """
        Account Fees

        See the fees applied to your withdrawals

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/account_fees',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def summary(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-summary
        """
        Summary

        Returns a 30-day summary of your trading volume and return on margin funding.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/summary',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def deposit_new(self, method, wallet_name, renew=0, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-deposit
        """
        Deposit

        Return your deposit address to make a new deposit.

        :param str method: Method of deposit (methods accepted: "bitcoin", "litecoin", "ethereum", "tetheruso",
            "ethereumc", "zcash", "monero", "iota", "bcash").
        :param str wallet_name: Wallet to deposit in (accepted: "trading", "exchange", "deposit"). Your wallet needs to
            already exist
        :param int renew: Default is 0. If set to 1, will return a new unused deposit address
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/deposit/new',
            path_params={
                'version': 1,
            },
            data={
                'method': method,
                'wallet_name': wallet_name,
                'renew': renew,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def key_info(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#auth-key-permissions
        """
        Key Permissions

        Check the permissions of the key being used to generate this request.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/key_info',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def margin_infos(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-margin-information
        """
        Margin Information

        See your trading wallet information for margin trading.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/margin_infos',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 20)
    @RateLimit(calls=20, period=60)  # Documentation states: 20 req/min
    def balances(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-wallet-balances
        """
        Wallet Balances

        See your balances

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/balances',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def transfer(self, amount, currency, walletfrom, walletto, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-transfer-between-wallets
        """
        Transfer Between Wallets

        Allow you to move available balances between your wallets.

        :param float amount: Amount to transfer
        :param str currency: Currency of funds to transfer.
        :param str walletfrom: Wallet to transfer from. Can be "trading", "deposit" or "exchange"
        :param str walletto: Wallet to transfer to. Can be "trading", "deposit" or "exchange"
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/transfer',
            path_params={
                'version': 1,
            },
            data={
                'amount': amount,
                'currency': currency,
                'walletfrom': walletfrom,
                'walletto': walletto,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def withdraw(self, withdraw_type, walletselected, amount, address, payment_id=None, account_name=None,
                 account_number=None, swift=None, bank_name=None, bank_address=None, bank_city=None, bank_country=None,
                 detail_payment=None, express_wire=None, intermediary_bank_name=None, intermediary_bank_address=None,
                 intermediary_bank_city=None, intermediary_bank_country=None, intermediary_bank_account=None,
                 intermediary_bank_swift=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-withdrawal
        """
        Withdrawal

        Allow you to request a withdrawal from one of your wallet.

        :param str withdraw_type: can be one of the following ['bitcoin', 'litecoin', 'ethereum', 'ethereumc',
            'mastercoin', 'zcash', 'monero', 'wire', 'dash', 'ripple', 'eos', 'neo', 'aventus', 'qtum', 'eidoo']
        :param str walletselected: The wallet to withdraw from, can be "trading", "exchange", or "deposit".
        :param str amount: Amount to withdraw
        :param str address: Destination address for withdrawal.
        :param str payment_id: Optional hex string to identify a Monero transaction
        :param str account_name: Account name
        :param str account_number: Account number
        :param str swift: The SWIFT code for your bank
        :param str bank_name: Bank name
        :param str bank_address: Bank address
        :param str bank_city: Bank city
        :param str bank_country: Bank country
        :param str detail_payment: Message to beneficiary
        :param int express_wire: "1" to submit an express wire withdrawal, "0" or omit for a normal withdrawal
        :param str intermediary_bank_name: Intermediary bank name
        :param str intermediary_bank_address: Intermediary bank address
        :param str intermediary_bank_city: Intermediary bank city
        :param str intermediary_bank_country: Intermediary bank country
        :param str intermediary_bank_account: Intermediary bank account
        :param str intermediary_bank_swift: Intermediary bank SWIFT
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/withdraw',
            path_params={
                'version': 1,
            },
            data={
                'withdraw_type': withdraw_type,
                'walletselected': walletselected,
                'amount': amount,
                'address': address,
                'payment_id': payment_id,
                'account_name': account_name,
                'account_number': account_number,
                'swift': swift,
                'bank_name': bank_name,
                'bank_address': bank_address,
                'bank_city': bank_city,
                'bank_country': bank_country,
                'detail_payment': detail_payment,
                'express_wire': express_wire,
                'intermediary_bank_name': intermediary_bank_name,
                'intermediary_bank_address': intermediary_bank_address,
                'intermediary_bank_city': intermediary_bank_city,
                'intermediary_bank_country': intermediary_bank_country,
                'intermediary_bank_account': intermediary_bank_account,
                'intermediary_bank_swift': intermediary_bank_swift,
            },
            credentials=credentials,
        )

        return response

    # Orders

    @RateLimit(calls=45, period=60)
    def order_new(self, symbol, amount, price, side, type_, exchange=None, is_hidden=None, is_postonly=None,
                  use_all_available=None, ocoorder=None, buy_price_oco=None, sell_price_oco=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-new-order
        """
        New Order

        Submit a new Order

        :param str symbol: The name of the symbol (see symbols()).
        :param float amount: Order size: how much you want to buy or sell
        :param float price: Price to buy or sell at. Must be positive. Use random number for market orders.
        :param str side: Either "buy" or "sell".
        :param str type_: Either "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill" / "exchange market" /
            "exchange limit" / "exchange stop" / "exchange trailing-stop" / "exchange fill-or-kill". (type starting by
            "exchange " are exchange orders, others are margin trading orders)
        :param str exchange:
        :param bool is_hidden: true if the order should be hidden.
        :param bool is_postonly: true if the order should be post only. Only relevant for limit orders.
        :param int use_all_available: 1 will post an order that will use all of your available balance.
        :param bool ocoorder: Set an additional STOP OCO order that will be linked with the current order.
        :param float buy_price_oco: If ocoorder is true, this field represent the price of the OCO stop order to place
        :param float sell_price_oco: If ocoorder is true, this field represent the price of the OCO stop order to place
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/new',
            path_params={
                'version': 1,
            },
            data={
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'side': side,
                'type_': type_,
                'exchange': exchange,
                'is_hidden': is_hidden,
                'is_postonly': is_postonly,
                'use_all_available': use_all_available,
                'ocoorder': ocoorder,
                'buy_price_oco': buy_price_oco,
                'sell_price_oco': sell_price_oco,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def order_new_multi(self, symbol, amount, price, side, type_, exchange=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-multiple-new-orders
        """
        Multiple New Orders

        Submit several new orders at once.

        :param str symbol: The name of the symbol (see symbols()).
        :param float amount: Order size: how much you want to buy or sell
        :param float price: Price to buy or sell at. Must be positive. Use random number for market orders.
        :param str side: Either "buy" or "sell".
        :param str type_: Either "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill".
        :param str exchange: "bitfinex"
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/new/multi',
            path_params={
                'version': 1,
            },
            data={
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'side': side,
                'type': type_,
                'exchange': exchange,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def order_cancel(self, order_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-cancel-order
        """
        Cancel Order

        Cancel an order.

        :param int order_id: The order ID given by order_new()
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/cancel',
            path_params={
                'version': 1,
            },
            data={
                'order_id': order_id,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def order_cancel_multi(self, order_ids, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-cancel-multiple-orders
        """
        Cancel Multiple Orders

        Cancel multiples orders at once.

        :param list(int) order_ids: An array of the order IDs given by order_new() or order_new_multi().
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/cancel/multi',
            path_params={
                'version': 1,
            },
            data={
                'order_ids': order_ids,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def order_cancel_all(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-cancel-all-orders
        """
        Cancel All Orders

        Cancel all active orders at once.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/cancel/all',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def order_cancel_replace(self, order_id, symbol=None, amount=None, price=None, exchange=None, side=None, type_=None,
                             is_hidden=None, is_postonly=None, use_remaining=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-replace-order
        """
        Replace Order

        Replace an order with a new one.

        :param int order_id: The order ID given by order_new().
        :param str symbol: The name of the symbol (see symbols()).
        :param int amount: Order size: how much to buy or sell.
        :param float price: Price to buy or sell at. May omit if a market order.
        :param str exchange: "bitfinex"
        :param str side: Either "buy" or "sell".
        :param str type_: Either "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill" / "exchange market" /
            "exchange limit" / "exchange stop" / "exchange trailing-stop" / "exchange fill-or-kill". (type starting by
            "exchange " are exchange orders, others are margin trading orders)
        :param bool is_hidden: true if the order should be hidden.
        :param bool is_postonly: true if the order should be post only. Only relevant for limit orders.
        :param bool use_remaining: True if the new order should use the remaining amount of the original order.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/cancel/replace',
            path_params={
                'version': 1,
            },
            data={
                'order_id': order_id,
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'exchange': exchange,
                'side': side,
                'type_': type_,
                'is_hidden': is_hidden,
                'is_postonly': is_postonly,
                'use_remaining': use_remaining,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def order_status(self, order_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-order-status
        """
        Order Status

        Get the status of an order. Is it active? Was it cancelled? To what extent has it been executed? etc.

        :param int order_id: The order ID given by order_new()
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/order/status',
            path_params={
                'version': 1,
            },
            data={
                'order_id': order_id,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def orders(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-active-orders
        """
        Active Orders

        View your active orders.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/orders',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 1)
    @RateLimit(calls=1, period=60)  # Documentation states: 1 req/min
    def orders_hist(self, limit=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-orders-history
        """
        Orders History

        View your latest inactive orders.
        Limited to last 3 days and 1 request per minute.

        :param int limit: Limit number of results

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/orders/hist',
            path_params={
                'version': 1,
            },
            data={
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    # Positions

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def positions(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-active-positions
        """
        Active Positions

        View your active positions.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/positions',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def positions_claim(self, position_id, amount, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-claim-position
        """
        Claim Position

        A position can be claimed if:

        It is a long position: The amount in the last unit of the position pair that you have in your trading wallet
        AND/OR the realized profit of the position is greater or equal to the purchase amount of the position (base
        price position amount) and the funds which need to be returned. For example, for a long BTCUSD position, you can
        claim the position if the amount of USD you have in the trading wallet is greater than the base price the
        position amount and the funds used.

        It is a short position: The amount in the first unit of the position pair that you have in your trading wallet
        is greater or equal to the amount of the position and the margin funding used.

        :param int position_id: The position ID given by positions()
        :param float amount: The partial amount you wish to claim.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/position/claim',
            path_params={
                'version': 1,
            },
            data={
                'position_id': position_id,
                'amount': amount,
            },
            credentials=credentials,
        )

        return response

    # Historical Data

    @Memoize(expires=60. / 20)
    @RateLimit(calls=20, period=60)  # Documentation states: 20 req/min
    def history(self, currency, since=None, until=None, limit=None, wallet=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-balance-history
        """
        Balance History

        View all of your balance ledger entries.

        :param str currency: The currency to look for.
        :param since: Return only the history after this timestamp.
        :param until: Return only the history before this timestamp.
        :param int limit: Limit the number of entries to return.
        :param str wallet: Return only entries that took place in this wallet. Accepted inputs are: "trading",
            "exchange", "deposit".
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/history',
            path_params={
                'version': 1,
            },
            data={
                'currency': currency,
                'since': since,
                'until': until,
                'limit': limit,
                'wallet': wallet,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 20)
    @RateLimit(calls=20, period=60)  # Documentation states: 20 req/min
    def history_movements(self, currency, method=None, since=None, until=None, limit=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-deposit-withdrawal-history
        """
        Deposit-Withdrawal History

        View your past deposits/withdrawals.

        :param str currency: The currency to look for.
        :param str method: The method of the deposit/withdrawal (can be "bitcoin", "litecoin", "darkcoin", "wire").
        :param since: Return only the history after this timestamp.
        :param until: Return only the history before this timestamp.
        :param int limit: Limit the number of entries to return.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/history/movements',
            path_params={
                'version': 1,
            },
            data={
                'currency': currency,
                'method': method,
                'since': since,
                'until': until,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)  # Documentation states: 45 req/min
    def mytrades(self, symbol, timestamp=None, until=None, limit_trades=None, reverse=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-past-trades
        """
        Past Trades

        View you past trades.

        :param str symbol: The pair traded (BTCUSD, ...).
        :param timestamp: Trades made before this timestamp won't be returned.
        :param until: Trade made after this timestamp won't be returned.
        :param int limit_trades: Limit the number of trades returned.
        :param int reverse: Return trades in reverse order (the oldest comes first). Default is returning newest trades
            first.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/mytrades',
            path_params={
                'version': 1,
            },
            data={
                'symbol': symbol,
                'timestamp': timestamp,
                'until': until,
                'limit_trades': limit_trades,
                'reverse': reverse,
            },
            credentials=credentials,
        )

        return response

    # Margin Funding

    @RateLimit(calls=45, period=60)
    def offer_new(self, currency, amount, rate, period, direction, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-new-offer
        """
        New Offer

        Submit a new Offer

        :param str currency: The name of the currency.
        :param float amount: Order size: how much to lend or borrow.
        :param float rate: Rate to lend or borrow at. In percentage per 365 days. (Set to 0 for FRR).
        :param int period: Number of days of the funding contract (in days)
        :param str direction: Either "lend" or "loan".
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/offer/new',
            path_params={
                'version': 1,
            },
            data={
                'currency': currency,
                'amount': amount,
                'rate': rate,
                'period': period,
                'direction': direction,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def offer_cancel(self, offer_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-cancel-offer
        """
        Cancel Offer

        Cancel an offer.
        
        :param int offer_id: The offer ID given by offer_new().
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/offer/cancel',
            path_params={
                'version': 1,
            },
            data={
                'order_id': offer_id,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def offer_status(self, offer_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-offer-status
        """
        Offer Status

        Get the status of an offer. Is it active? Was it cancelled? To what extent has it been executed? etc.
        
        :param int offer_id: The offer ID given by offer_new().
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/offer/status',
            path_params={
                'version': 1,
            },
            data={
                'offer_id': offer_id,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def credits(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-active-credits
        """
        Active Credits

        View your funds currently taken (active credits).

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/credits',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def offers(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-offers
        """
        Offers

        View your active offers.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/offers',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 1)
    @RateLimit(calls=1, period=60)  # Documentation states: 1 req/min
    def offer_hist(self, limit=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-offers-hist
        """
        Offers History

        View your latest inactive offers.
        Limited to last 3 days and 1 request per minute.
        
        :param int limit: Limit number of results
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/offers/hist',
            path_params={
                'version': 1,
            },
            data={
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)  # Documentation states: 45 req/min
    def mytrades_funding(self, symbol, until=None, limit_trades=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-mytrades-funding
        """
        Past Funding Trades

        View your past trades.

        :param str symbol: The pair traded (USD, ...).
        :param until: Trades made after this timestamp won't be returned.
        :param int limit_trades: Limit the number of trades returned.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/mytrades_funding',
            path_params={
                'version': 1,
            },
            data={
                'symbol': symbol,
                'until': until,
                'limit_trades': limit_trades,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def taken_funds(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-active-funding-used-in-a-margin-position
        """
        Active Funding Used in a margin position

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/taken_funds',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def unused_taken_funds(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-active-funding-not-used-in-a-margin-position
        """
        Active Funding Not Used in a margin position

        View your funding currently borrowed and not used (available for a new margin position).

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/unused_taken_funds',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def total_taken_funds(self, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-total-taken-funds
        """
        Total Taken Funds

        View the total of your active funding used in your position(s).

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/total_taken_funds',
            path_params={
                'version': 1,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def funding_close(self, swap_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#rest-auth-close-margin-funding
        """
        Close Margin Funding

        Allow you to close an unused or used taken fund

        :param int swap_id: The ID given by taken_funds() or unused_taken_funds()
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/funding/close',
            path_params={
                'version': 1,
            },
            data={
                'swap_id': swap_id,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def basket_manage(self, amount=None, dir_=None, name=None, credentials=None):
        # https://docs.bitfinex.com/v1/reference#basket-manage
        """
        Basket Manage

        This endpoint is used to manage the creation or destruction of tokens via splitting or merging. For the moment,
        this is only useful for the bcc and bcu tokens.

        :param str amount: The amount you wish to split or merge
        :param int dir_: 1 to split, -1 to merge
        :param str name: the symbol of the token pair you wish to create or destroy
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/basket_manage',
            path_params={
                'version': 1,
            },
            data={
                'amount': amount,
                'dir': dir_,
                'name': name,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def positions_close(self, position_id, credentials=None):
        # https://docs.bitfinex.com/v1/reference#close-position
        """
        Close Position

        Closes the selected position with a market order.

        :param int position_id: The position ID given by positions().
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/position/close',
            path_params={
                'version': 1,
            },
            data={
                'position_id': position_id,
            },
            credentials=credentials,
        )

        return response

    #
    # V2 Public Endpoints
    #

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def platform_status(self):
        # https://docs.bitfinex.com/v2/reference#rest-public-platform-status
        """
        Platform Status

        Get the current status of the platform.
        Maintenance periods last for just few minutes and might be necessary from time to time during upgrades of core
        components of our infrastructure.
        Even if rare it is important to have a way to notify users.
        For a real-time notification we suggest to use websockets and listen to events 20060/20061

        Maintenance mode
        When the platform is marked in maintenance mode bots should stop trading activity. Cancelling orders will be
        still possible.
        """

        response = self.request(
            method='GET',
            path='v{version}/platform/status',
            path_params={
                'version': 2,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def tickers(self, symbols):
        # https://docs.bitfinex.com/v2/reference#rest-public-tickers
        """
        Tickers

        The ticker is a high level overview of the state of the market. It shows you the current best bid and ask, as
        well as the last trade price. It also includes information such as daily volume and how much the price has moved
        over the last day.

        :param str symbols: The symbols you want information about. ex: tBTCUSD,fUSD
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/tickers',
            path_params={
                'version': 2,
            },
            query_params={
                'symbols': symbols,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def ticker(self, symbol):
        # https://docs.bitfinex.com/v2/reference#rest-public-ticker
        """
        Ticker

        The ticker is a high level overview of the state of the market. It shows you the current best bid and ask, as
        well as the last trade price. It also includes information such as daily volume and how much the price has moved
        over the last day.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            /symbols endpoint.
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/ticker/{symbol}',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def trades_hist(self, symbol, limit=120, start=None, end=None, sort=-1):
        # https://docs.bitfinex.com/v2/reference#rest-public-trades
        """
        Trades

        Trades endpoint includes all the pertinent details of the trade, such as price, size and time.

        :param str symbol: The symbol you want information about.
        :param int limit: Number of records
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int sort: if = 1 it sorts results returned with old > new
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/trades/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'limit': limit,
                'start': start,
                'end': end,
                'sort': sort,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def book_v2(self, symbol, precision='P0', len_=25):
        # https://docs.bitfinex.com/v2/reference#rest-public-books
        """
        Books

        The Order Books channel allow you to keep track of the state of the Bitfinex order book.
        It is provided on a price aggregated basis, with customizable precision.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            /symbols endpoint.
        :param str precision: Level of price aggregation (P0, P1, P2, P3, R0)
        :param int len_: Number of price points ("25", "100")
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/book/{symbol}/{precision}',
            path_params={
                'version': 2,
                'symbol': symbol,
                'precision': precision,
            },
            query_params={
                'len': len_,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def stats1(self, key='', size='', symbol='', side='', section='', sort=None):
        # https://docs.bitfinex.com/v2/reference#rest-public-stats
        """
        Stats

        Various statistics about the requested pair.

        :param str key: Allowed values: "funding.size", "credits.size", "credits.size.sym", "pos.size"
        :param str size: Available values: '1m'
        :param str symbol: The symbol you want information about.
        :param str side: Available values: "long", "short"
        :param str section: Available values: "last", "hist"
        :param int sort: if = 1 it sorts results returned with old > new
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/stats1/{key}:{size}:{symbol}:{side}/{section}',
            path_params={
                'version': 2,
                'key': key,
                'size': size,
                'symbol': symbol,
                'side': side,
                'section': section,
            },
            query_params={
                'sort': sort,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def candles(self, timeframe, symbol, section, limit=None, start=None, end=None, sort='-1'):
        # https://docs.bitfinex.com/v2/reference#rest-public-candles
        """
        Candles

        Provides a way to access charting candle info

        :param str timeframe: Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D',
            '1M'
        :param str symbol: The symbol you want information about.
        :param str section: Available values: "last", "hist"
        :param int limit: Number of candles requested
        :param str start: Filter start (ms)
        :param str end: Filter end (ms)
        :param int sort: if = 1 it sorts results returned with old > new
        :return:
        """

        response = self.request(
            method='GET',
            path='v{version}/candles/trade:{timeframe}:{symbol}/{section}',
            path_params={
                'version': 2,
                'timeframe': timeframe,
                'symbol': symbol,
                'section': section,
            },
            query_params={
                'limit': limit,
                'start': start,
                'end': end,
                'sort': sort,
            },
        )

        return response

    #
    # V2 Calculation Endpoints
    #

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def calc_market_average_price(self, symbol, amount=None, period=None, rate_limit=None):
        # https://docs.bitfinex.com/v2/reference#rest-calc-market-average-price
        """
        Market Average Price

        Calculate the average execution rate for Trading or Margin funding.

        :param str symbol: The symbol you want information about.
        :param str amount: Amount. Positive for buy, negative for sell (ex. "1.123")
        :param int period: (optional) Maximum period for Margin Funding
        :param str rate_limit: Limit rate/price (ex. "1000.5")
        :return:
        """

        response = self.request(
            method='POST',
            path='v{version}/calc/trade/avg',
            path_params={
                'version': 2,
            },
            query_params={
                'symbol': symbol,
                'amount': amount,
                'period': period,
                'rate_limit': rate_limit,
            },
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def foreign_exchange_rate(self, ccy1, ccy2):
        # https://docs.bitfinex.com/v2/reference#foreign-exchange-rate
        """
        Foreign Exchange Rate

        :param str ccy1: First currency
        :param str ccy2: Second currency
        :return:
        """

        response = self.request(
            method='POST',
            path='v{version}/calc/fx',
            path_params={
                'version': 2,
            },
            data={
                'ccy1': ccy1,
                'ccy2': ccy2,
            },
        )

        return response

    #
    # V2 Authenticated Endpoints
    #

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_wallets(self, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-wallets
        """
        Wallets

        Get account wallets

        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/wallets',
            path_params={
                'version': 2,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_orders(self, symbol=None, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-orders
        """
        Orders

        Get active orders

        :param symbol:
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/orders/{symbol}',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_orders_history(self, symbol, start=None, end=None, limit=25, sort=-1, credentials=None):
        # https://docs.bitfinex.com/v2/reference#orders-history
        """
        Orders History

        Returns the most recent closed or canceled orders up to circa two weeks ago

        :param str symbol: Symbol (tBTCUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: Number of records
        :param int sort: set to 1 to get results in ascending order
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/orders/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
                'sort': sort,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_order_trades(self, symbol, order_id, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-order-trades
        """
        Order Trades

        Get Trades generated by an Order

        :param str symbol: Symbol
        :param int order_id: Order id
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/order/{symbol}:{order_id}/trades',
            path_params={
                'version': 2,
                'symbol': symbol,
                'order_id': order_id,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_trades(self, symbol, start=None, end=None, limit=25, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-trades-hist
        """
        Trades

        Get trades

        :param str symbol: Symbol (tBTCUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: Number of records
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/trades/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_positions(self, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-positions
        """
        Positions

        Get active positions

        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/positions',
            path_params={
                'version': 2,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_offers(self, symbol, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-offers
        """
        Funding Offers

        Get active funding offers

        :param symbol: Symbol (fUSD, ...)
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/offers/{symbol}',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_offers_hist(self, symbol, start=None, end=None, limit=25, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-offers-hist
        """
        Funding Offers History

        Get past inactive funding offers. Limited to last 3 days.

        :param str symbol: Symbol (fUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: Number of records
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/offers/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_loans(self, symbol, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-loans
        """
        Funding Loans

        Funds not used in active positions

        :param str symbol: Symbol (fUSD, ...)
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/loans/{symbol}',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_loans_hist(self, symbol, start=None, end=None, limit=25, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-loans-hist
        """
        Funding Loans History

        Inactive funds not used in positions. Limited to last 3 days.

        :param str symbol: Symbol (fUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: Number of records
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/loans/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_credits(self, symbol, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-credits
        """
        Funding Credits

        Funds used in active positions

        :param str symbol: Symbol (fUSD, ...)
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/credits/{symbol}',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_credits_hist(self, symbol, start=None, end=None, limit=25, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-credits-hist
        """
        Funding Credits History

        Inactive funds used in positions. Limited to last 3 days.

        :param str symbol: Symbol (fUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: 25
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/credits/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_funding_trades_hist(self, symbol, start=None, end=None, limit=None, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-funding-trades-hist
        """
        Funding Trades

        Get funding trades

        :param str symbol: Symbol (tBTCUSD, ...)
        :param int start: Millisecond start time
        :param int end: Millisecond end time
        :param int limit: Number of records
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/funding/trades/{symbol}/hist',
            path_params={
                'version': 2,
                'symbol': symbol,
            },
            query_params={
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_info_margin(self, key, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-info-margin
        """
        Margin Info

        Get account margin info

        :param str key: "base" | SYMBOL
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/info/margin/{key}',
            path_params={
                'version': 2,
                'key': key,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_info_funding(self, key, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-info-funding
        """
        Funding Info

        Get account funding info

        :param str key: SYMBOL
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/info/funding/{key}',
            path_params={
                'version': 2,
                'key': key,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_movements_hist(self, currency, credentials=None):
        # https://docs.bitfinex.com/v2/reference#movements
        """
        Movements

        View your past deposits/withdrawals.

        :param str currency: Currency (BTC, ...)
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/movements/{currency}/hist',
            path_params={
                'version': 2,
                'currency': currency,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_stats_perf_hist(self, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-performance
        """
        Performance

        Get account historical daily performance (work in progress)

        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/stats/perf:1D/hist',
            path_params={
                'version': 2,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_alerts(self, type_='price', credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-alert-list
        """
        Alert List


        :param str type_:
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/stats/perf:1D/hist',
            path_params={
                'version': 2,
            },
            query_params={
                'type': type_,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def auth_alert_set(self, type_, symbol, price, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-alert-set
        """
        Alert Set

        Sets up a price alert at the given value

        :param str type_:
        :param str symbol:
        :param int price:
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/w/alert/set',
            path_params={
                'version': 2,
            },
            query_params={
                'type': type_,
                'symbol': symbol,
                'price': price,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def auth_alert_del(self, symbol, price, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-alert-delete
        """
        Alert Delete

        :param str symbol:
        :param int price:
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/w/alert/price:{symbol}:{price}/del',
            path_params={
                'version': 2,
                'symbol': symbol,
                'price': price,
            },
            credentials=credentials,
        )

        return response

    @RateLimit(calls=45, period=60)
    def auth_calc_order_avail(self, symbol, dir_, rate, type_, credentials=None):
        # https://docs.bitfinex.com/v2/reference#rest-auth-calc-bal-avail
        """
        Calc Available Balance

        Calculate available balance for order/offer

        :param str symbol: Symbol
        :param int dir_: direction of the order/offer (orders: > 0 buy, < 0 sell | offers: > 0 sell, < 0 buy)
        :param str rate: Rate of the order/offer
        :param str type_: Type of the order/offer EXCHANGE or MARGIN
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/calc/order/avail',
            path_params={
                'version': 2,
            },
            query_params={
                'symbol': symbol,
                'dir': dir_,
                'rate': rate,
                'type': type_,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_ledgers_hist(self, currency, credentials=None):
        # https://docs.bitfinex.com/v2/reference#ledgers
        """
        Ledgers

        View your past ledger entries

        :param str currency: Currency (BTC, ...)
        :param dict credentials: dictionary containing authentication information like key and secret
        :return:
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='v{version}/auth/r/ledgers/{currency}/hist',
            path_params={
                'version': 2,
                'currency': currency,
            },
            credentials=credentials,
        )

        return response

    @Memoize(expires=60. / 45)
    @RateLimit(calls=45, period=60)
    def auth_settings_read(self, *args, **kwargs):
        # https://docs.bitfinex.com/v2/reference#user-settings-read
        raise NotImplementedError

    @RateLimit(calls=45, period=60)
    def auth_settings_set(self, *args, **kwargs):
        # https://docs.bitfinex.com/v2/reference#user-settings-write
        raise NotImplementedError

    @RateLimit(calls=45, period=60)
    def auth_settings_del(self, *args, **kwargs):
        # https://docs.bitfinex.com/v2/reference#user-settings-delete
        raise NotImplementedError
