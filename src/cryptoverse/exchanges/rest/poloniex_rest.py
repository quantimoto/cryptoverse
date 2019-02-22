import hashlib
import hmac
import json
from json.decoder import JSONDecodeError
from urllib.parse import urlencode

from requests import ReadTimeout, ConnectionError

from cryptoverse.utilities.decorators import formatter, Retry, RateLimit, Memoize
from ...base.rest import RESTClient
from ...exceptions import MissingCredentialsException, ExchangeDecodeException, ExchangeException


class PoloniexREST(RESTClient):
    # https://docs.poloniex.com/
    """
    Complete implementation of the Poloniex REST-api as documented at:
    https://poloniex.com/support/api/
    """

    host = 'poloniex.com'
    uri_template = '/{endpoint}'

    credentials = None

    # Authentication methods

    def sign(self, request_obj, credentials):
        """
        Signs the request object using the supplied credentials according to Poloniex's requirements.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """
        payload = request_obj.data
        payload.update({
            'nonce': self.nonce(),
        })

        encoded_payload = urlencode(payload).encode('utf-8')
        message = encoded_payload

        h = hmac.new(
            key=credentials.secret.encode('utf-8'),
            msg=message,
            digestmod=hashlib.sha512,
        )
        signature = h.hexdigest()

        headers = {
            'Key': credentials.key,
            'Sign': signature,
        }
        request_obj.headers = headers
        request_obj.data = payload

        return request_obj

    @Retry(ReadTimeout, wait=60)
    @Retry(ConnectionError, wait=60)
    @RateLimit(calls=6, period=1)  # Documentation states: 6 req/sec
    @formatter
    def request(self, *args, **kwargs):
        result = super(self.__class__, self).request(*args, **kwargs)

        try:
            result_from_json = json.loads(result.text)
        except JSONDecodeError:
            print(result.text)
            raise ExchangeDecodeException

        if type(result_from_json) is dict and 'error' in result_from_json:
            raise ExchangeException(result_from_json)

        return result

    #
    # Public Endpoints
    #

    @Memoize(expires=1)
    def return_ticker(self):
        """
        Retrieves summary information for each currency pair listed on the exchange.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnTicker',
            },
        )

        return response

    @Memoize(expires=1)
    def return_24_volume(self):
        """
        Returns the 24-hour volume for all markets as well as totals for primary currencies.

        Primary currencies include BTC, ETH, USDT, USDC and XMR and show the total amount of those tokens that have
        traded within the last 24 hours.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'return24hVolume',
            },
        )

        return response

    @Memoize(expires=1)
    def return_order_book(self, currency_pair='all', depth=50):
        """
        Returns the order book for a given market, as well as a sequence number used by websockets for synchronization
        of book updates and an indicator specifying whether the market is frozen. You may set currency_pair to "all" to
        get the order books of all markets.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnOrderBook',
                'currencyPair': currency_pair,
                'depth': depth,
            },
        )

        return response

    @Memoize(expires=1)
    def return_trade_history_public(self, currency_pair, start=None, end=None, limit=None):
        """
        Returns the past 200 trades for a given market, or up to 50,000 trades between a range specified in UNIX
        timestamps by the "start" and "end" GET parameters.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnTradeHistory',
                'currencyPair': currency_pair,
                'start': start,
                'end': end,
                'limit': limit,
            },
        )

        return response

    @Memoize(expires=1)
    def return_chart_data(self, currency_pair, period=None, start=None, end=None):
        """
        Returns candlestick chart data. Required GET parameters are "currencyPair", "period" (candlestick period in
        seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400), "start", and "end". "Start" and "end" are
        given in UNIX timestamp format and used to specify the date range for the data returned.

        :param str currency_pair: The currency pair of the market being requested.
        :param int period: Candlestick period in seconds. Valid values are 300, 900, 1800, 7200, 14400, and 86400.
        :param int start: The start of the window in seconds since the unix epoch.
        :param int end: The end of the window in seconds since the unix epoch.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnChartData',
                'currencyPair': currency_pair,
                'period': period,
                'start': start,
                'end': end,
            },
        )

        return response

    @Memoize(expires=1)
    def return_currencies(self):
        """
        Returns information about currencies.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnCurrencies',
            },
        )

        return response

    @Memoize(expires=1)
    def return_loan_orders(self, currency=None, limit=None):
        """
        Returns the list of loan offers and demands for a given currency, specified by the "currency" GET
        parameter.
        """

        response = self.request(
            method='GET',
            path='public',
            query_params={
                'command': 'returnLoanOrders',
                'currency': currency,
                'limit': limit,
            },
        )

        return response

    #
    # Authenticated Endpoints
    #

    def return_balances(self, credentials=None):
        """
        Returns all of your balances available for trade after having deducted all open orders.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnBalances',
            },
            credentials=credentials,
        )

        return response

    def return_complete_balances(self, account=None, credentials=None):
        """
        Returns all of your balances, including available balance, balance on orders, and the estimated BTC value of
        your balance. By default, this call is limited to your exchange account; set the "account" POST parameter to
        "all" to include your margin and lending accounts.

        :param str account: Set this to "all" to include your margin and lending accounts.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnCompleteBalances',
                'account': account,
            },
            credentials=credentials,
        )

        return response

    def return_deposit_addresses(self, credentials=None):
        """
        Returns all of your deposit addresses.

        Some currencies use a common deposit address for everyone on the exchange and designate the account for which
        this payment is destined by including a payment ID field. In these cases, use returnCurrencies to look up the
        mainAccount for the currency to find the deposit address and use the address returned here in the payment ID
        field. Note: returnCurrencies will only include a mainAccount property for currencies which require a payment
        ID.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnDepositAddresses',
            },
            credentials=credentials,
        )

        return response

    def generate_new_address(self, currency=None, credentials=None):
        """
        Generates a new deposit address for the currency specified by the "currency" POST parameter. Only one address
        per currency per day may be generated, and a new address may not be generated before the previously-generated
        one has been used.

        Some currencies use a common deposit address for everyone on the exchange and designate the account for which
        this payment is destined by including a payment ID field. In these cases, use returnCurrencies to look up the
        mainAccount for the currency to find the deposit address and use the address returned here in the payment ID
        field. Note: returnCurrencies will only include a mainAccount property for currencies which require a payment
        ID.

        :param str currency: The currency to use for the deposit address.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'generateNewAddress',
                'currency': currency,
            },
            credentials=credentials,
        )

        return response

    def return_deposits_withdrawals(self, start, end, credentials=None):
        """
        Returns your deposit and withdrawal history within a range window, specified by the "start" and "end" POST
        parameters, both of which should be given as UNIX timestamps.

        :param int start: The start date of the range window in UNIX timestamp format.
        :param int end: The end date of the range window in UNIX timestamp format.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnDepositsWithdrawals',
                'start': start,
                'end': end,
            },
            credentials=credentials,
        )

        return response

    def return_open_orders(self, currency_pair, credentials=None):
        """
        Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_ETH". Set
        "currencyPair" to "all" to return open orders for all markets.

        :param str currency_pair: The major and minor currency that define this market. (or 'all' for all markets)
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnOpenOrders',
                'currencyPair': currency_pair,
            },
            credentials=credentials,
        )

        return response

    def return_trade_history_private(self, currency_pair=None, start=None, end=None, limit=None, credentials=None):
        """
        Returns your trade history for a given market, specified by the "currencyPair" POST parameter. You may specify
        "all" as the currencyPair to receive your trade history for all markets. You may optionally specify a range via
        "start" and/or "end" POST parameters, given in UNIX timestamp format; if you do not specify a range, it will be
        limited to one day. You may optionally limit the number of entries returned using the "limit" parameter, up to a
        maximum of 10,000. If the "limit" parameter is not specified, no more than 500 entries will be returned.

        :param str currency_pair: The major and minor currency that define this market. (or 'all' for all markets)
        :param int start: The start date of the range window in UNIX timestamp format.
        :param int end: The end date of the range window in UNIX timestamp format.
        :param int limit: You may optionally limit the number of entries returned using the "limit" parameter, up to a
        maximum of 10,000. If the "limit" parameter is not specified, no more than 500 entries will be returned.
        :param dict credentials: dictionary containing authentication information like key and secret

        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnTradeHistory',
                'currencyPair': currency_pair,
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    def return_order_trades(self, order_number, credentials=None):
        """
        Returns all trades involving a given order, specified by the "orderNumber" POST parameter. If no trades for the
        order have occurred or you specify an order that does not belong to you, you will receive an error. See the
        documentation here for how to use the information from returnOrderTrades and returnOrderStatus to determine
        various status information about an order.

        :param int order_number: The order number whose trades you wish to query.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnOrderTrades',
                'orderNumber': order_number,
            },
            credentials=credentials,
        )

        return response

    def return_order_status(self, order_number, credentials=None):
        """
        Returns the status of a given order, specified by the "orderNumber" POST parameter. If the specified orderNumber
        is not open, or it is not yours, you will receive an error.

        Note that returnOrderStatus, in concert with returnOrderTrades, can be used to determine various status
        information about an order:

        - If returnOrderStatus returns status: "Open", the order is fully open.
        - If returnOrderStatus returns status: "Partially filled", the order is partially filled, and returnOrderTrades
        may be used to find the list of those fills.
        - If returnOrderStatus returns an error and returnOrderTrades returns an error, then the order was cancelled
        before it was filled.
        - If returnOrderStatus returns an error and returnOrderTrades returns a list of trades, then the order had fills
        and is no longer open (due to being completely filled, or partially filled and then cancelled).

        :param int order_number: The identifier of the order to return.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnOrderStatus',
                'orderNumber': order_number,
            },
            credentials=credentials,
        )

        return response

    def buy(self, currency_pair, rate, amount, fill_or_kill=None, immediate_or_cancel=None, post_only=None,
            credentials=None):
        """
        Places a limit buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        If successful, the method will return the order number.

        You may optionally set "fillOrKill", "immediateOrCancel", "postOnly" to 1. A fill-or-kill order will either fill
        in its entirety or be completely aborted. An immediate-or-cancel order can be partially or completely filled,
        but any portion of the order that cannot be filled immediately will be canceled rather than left on the order
        book. A post-only order will only be placed if no portion of it fills immediately; this guarantees you will
        never pay the taker fee on any part of the order that fills.

        :param str currency_pair: The major and minor currency defining the market where this buy order should be
        placed.
        :param float rate: The rate to purchase one major unit for this trade.
        :param float amount: The total amount of minor units offered in this buy order.
        :param int fill_or_kill: (optional) Set to "1" if this order should either fill in its entirety or be completely
        aborted.
        :param int immediate_or_cancel: (optional) Set to "1" if this order can be partially or completely filled, but
        any portion of the order that cannot be filled immediately will be canceled.
        :param int post_only: (optional) Set to "1" if you want this buy order to only be placed if no portion of it
        fills immediately.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'buy',
                'currencyPair': currency_pair,
                'rate': rate,
                'amount': amount,
                'fillOrKill': fill_or_kill,
                'immediateOrCancel': immediate_or_cancel,
                'postOnly': post_only,
            },
            credentials=credentials,
        )

        return response

    def sell(self, currency_pair, rate, amount, fill_or_kill=None, immediate_or_cancel=None, post_only=None,
             credentials=None):
        """
        Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If
        successful, the method will return the order number.

        You may optionally set "fillOrKill", "immediateOrCancel", "postOnly" to 1. A fill-or-kill order will either fill
        in its entirety or be completely aborted. An immediate-or-cancel order can be partially or completely filled,
        but any portion of the order that cannot be filled immediately will be canceled rather than left on the order
        book. A post-only order will only be placed if no portion of it fills immediately; this guarantees you will
        never pay the taker fee on any part of the order that fills.

        :param str currency_pair: The major and minor currency defining the market where this buy order should be
        placed.
        :param float rate: The rate to purchase one major unit for this trade.
        :param float amount: The total amount of minor units offered in this buy order.
        :param int fill_or_kill: (optional) Set to "1" if this order should either fill in its entirety or be completely
        aborted.
        :param int immediate_or_cancel: (optional) Set to "1" if this order can be partially or completely filled, but
        any portion of the order that cannot be filled immediately will be canceled.
        :param int post_only: (optional) Set to "1" if you want this buy order to only be placed if no portion of it
        fills immediately.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'sell',
                'currencyPair': currency_pair,
                'rate': rate,
                'amount': amount,
                'fillOrKill': fill_or_kill,
                'immediateOrCancel': immediate_or_cancel,
                'postOnly': post_only,
            },
            credentials=credentials,
        )

        return response

    def cancel_order(self, order_number, credentials=None):
        """
        Cancels an order you have placed in a given market. Required POST parameter are "currencyPair" and
        "orderNumber". If successful, the method will return a success of 1.

        :param order_number: The identity number of the order to be canceled.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'cancelOrder',
                'orderNumber': order_number,
            },
            credentials=credentials,
        )

        return response

    def move_order(self, order_number, rate, amount=None, post_only=None, immediate_or_cancel=None, credentials=None):
        """
        Cancels an order and places a new one of the same type in a single atomic transaction, meaning either both
        operations will succeed or both will fail. Required POST parameters are "orderNumber" and "rate"; you may
        optionally specify "amount" if you wish to change the amount of the new order. "postOnly" or "immediateOrCancel"
        may be specified for exchange orders, but will have no effect on margin orders.

        :param order_number: The identity number of the order to be canceled.
        :param float rate: The rate to purchase one major unit for this trade.
        :param float amount: (optional) The total amount of minor units offered in this buy order.
        :param int immediate_or_cancel: (optional) Set to "1" if this order can be partially or completely filled, but
        any portion of the order that cannot be filled immediately will be canceled.
        :param int post_only: (optional) Set to "1" if you want this buy order to only be placed if no portion of it
        fills immediately.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'moveOrder',
                'orderNumber': order_number,
                'rate': rate,
                'amount': amount,
                'immediateOrCancel': immediate_or_cancel,
                'post_only': post_only,
            },
            credentials=credentials,
        )

        return response

    def withdraw(self, currency, amount, address, payment_id=None, credentials=None):
        """
        Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method,
        withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and
        "address". For withdrawals which support payment IDs, (such as XMR) you may optionally specify "paymentId".

        :param str currency:
        :param float amount:
        :param str address:
        :param str payment_id:
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'withdraw',
                'currency': currency,
                'amount': amount,
                'address': address,
                'payment_id': payment_id,
            },
            credentials=credentials,
        )

        return response

    def return_fee_info(self, credentials=None):
        """
        If you are enrolled in the maker-taker fee schedule, returns your current trading fees and trailing 30-day
        volume in BTC. This information is updated once every 24 hours.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnFeeInfo',
            },
            credentials=credentials,
        )

        return response

    def return_available_account_balances(self, account=None, credentials=None):
        """
        Returns your balances sorted by account. You may optionally specify the "account" POST parameter if you wish to
        fetch only the balances of one account. Please note that balances in your margin account may not be accessible
        if you have any open margin positions or orders.

        :param str account: (optional) account to fetch. 'exchange', 'margin' or 'lending'.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnAvailableAccountBalances',
                'account': account,
            },
            credentials=credentials,
        )

        return response

    def return_tradable_balances(self, credentials=None):
        """
        Returns your current tradable balances for each currency in each market for which margin trading is enabled.
        Please note that these balances may vary continually with market conditions.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnTradableBalances',
            },
            credentials=credentials,
        )

        return response

    def transfer_balance(self, currency, amount, from_account, to_account, credentials=None):
        """
        Transfers funds from one account to another (e.g. from your exchange account to your margin account). Required
        POST parameters are "currency", "amount", "fromAccount", and "toAccount".

        :param str currency: The currency to transfer.
        :param float amount: The amount of assets to transfer in this request.
        :param str from_account: The account from which this value should be moved.
        :param str to_account: The account to which this value should be moved.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'transferBalance',
                'currency': currency,
                'amount': amount,
                'fromAccount': from_account,
                'toAccounnt': to_account,
            },
            credentials=credentials,
        )

        return response

    def return_margin_account_summary(self, credentials=None):
        """
        Returns a summary of your entire margin account. This is the same information you will find in the Margin
        Account section of the (Margin Trading page)[https://poloniex.com/support/aboutMarginTrading/], under the
        Markets list.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnMarginAccountSummary',
            },
            credentials=credentials,
        )

        return response

    def margin_buy(self, currency_pair, rate, amount, lending_rate=None, credentials=None):
        """
        Places a margin buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        You may optionally specify a maximum lending rate using the "lendingRate" parameter. If successful, the method
        will return the order number and any trades immediately resulting from your order.

        :param str currency_pair: The major and minor currency that define this market.
        :param float rate: The rate to purchase one major unit for this trade.
        :param float amount: The amount of currency to buy in minor currency units.
        :param int lending_rate: (optional) The interest rate you are willing to accept in percentage per day.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'marginBuy',
                'currencyPair': currency_pair,
                'rate': rate,
                'amount': amount,
                'lendingRate': lending_rate,
            },
            credentials=credentials,
        )

        return response

    def margin_sell(self, currency_pair, rate, amount, lending_rate=None, credentials=None):
        """
        Places a margin sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        You may optionally specify a maximum lending rate using the "lendingRate" parameter. If successful, the method
        will return the order number and any trades immediately resulting from your order.

        :param str currency_pair: The major and minor currency that define this market.
        :param float rate: The rate to purchase one major unit for this trade.
        :param float amount: The amount of currency to buy in minor currency units.
        :param int lending_rate: (optional) The interest rate you are willing to accept in percentage per day.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'marginSell',
                'currencyPair': currency_pair,
                'rate': rate,
                'amount': amount,
                'lendingRate': lending_rate,
            },
            credentials=credentials,
        )

        return response

    def get_margin_position(self, currency_pair, credentials=None):
        """
        Returns information about your margin position in a given market, specified by the "currencyPair" POST
        parameter. You may set "currencyPair" to "all" if you wish to fetch all of your margin positions at once. If you
        have no margin position in the specified market, "type" will be set to "none". "liquidationPrice" is an
        estimate, and does not necessarily represent the price at which an actual forced liquidation will occur. If you
        have no liquidation price, the value will be -1.

        :param int currency_pair: The major and minor currency that define this market.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'getMarginPosition',
                'currencyPair': currency_pair,
            },
            credentials=credentials,
        )

        return response

    def close_margin_position(self, currency_pair, credentials=None):
        """
        Closes your margin position in a given market (specified by the "currencyPair" POST parameter) using a market
        order. This call will also return success if you do not have an open position in the specified market.

        :param int currency_pair: The major and minor currency that define this market.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'closeMarginPosition',
                'currencyPair': currency_pair,
            },
            credentials=credentials,
        )

        return response

    def create_loan_offer(self, currency, amount, duration, auto_renew, lending_rate, credentials=None):
        """
        Creates a loan offer for a given currency. Required POST parameters are "currency", "amount", "duration",
        "autoRenew" (0 or 1), and "lendingRate".

        :param int currency: Denotes the currency for this loan offer.
        :param int amount: The total amount of currency offered.
        :param int duration: The maximum duration of this loan in days. (from 2 to 60, inclusive)
        :param int auto_renew: Denotes if this offer should be reinstated with the same settings after having been
        taken.
        :param int lending_rate:
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'createLoanOffer',
                'currency': currency,
                'amount': amount,
                'duration': duration,
                'auto_renew': auto_renew,
                'lending_rate': lending_rate,
            },
            credentials=credentials,
        )

        return response

    def cancel_loan_offer(self, order_number, credentials=None):
        """
        Cancels a loan offer specified by the "orderNumber" POST parameter.

        :param int order_number: The identification number of the offer to be canceled.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'cancelLoanOffer',
                'orderNumber': order_number,
            },
            credentials=credentials,
        )

        return response

    def return_open_loan_offers(self, credentials=None):
        """
        Returns your open loan offers for each currency.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnOpenLoanOffers',
            },
            credentials=credentials,
        )

        return response

    def return_active_loans(self, credentials=None):
        """
        Returns your active loans for each currency.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnActiveLoans',
            },
            credentials=credentials,
        )

        return response

    def return_lending_history(self, start=None, end=None, limit=None, credentials=None):
        """
        Returns your lending history within a time range specified by the "start" and "end" POST parameters as UNIX
        timestamps. "limit" may also be specified to limit the number of rows returned.

        :param int start: The date in Unix timestamp format of the start of the window.
        :param int end: The date in Unix timestamp format of the end of the window.
        :param int limit: (optional)
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'returnLendingHistory',
                'start': start,
                'end': end,
                'limit': limit,
            },
            credentials=credentials,
        )

        return response

    def toggle_auto_renew(self, order_number, credentials=None):
        """
        Toggles the autoRenew setting on an active loan, specified by the "orderNumber" POST parameter. If successful,
        "message" will indicate the new autoRenew setting.

        :param int order_number: The identifier of the order you want to toggle.
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsException

        response = self.request(
            method='POST',
            path='tradingApi',
            data={
                'command': 'toggleAutoRenew',
                'orderNumber': order_number,
            },
            credentials=credentials,
        )

        return response
