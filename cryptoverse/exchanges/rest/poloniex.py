import hashlib
import hmac
import urllib

from ...base.rest import RESTClient
from ...exceptions import MissingCredentialsError


class PoloniexREST(RESTClient):
    # https://poloniex.com/support/api/
    """
    Complete implementation of the Poloniex REST-api as documented at:
    https://poloniex.com/support/api/
    """

    address = 'https://poloniex.com'
    uri_template = '/{endpoint}'

    credentials = None

    # Authentication methods

    def sign(self, request_obj, credentials):
        """
        Signs the request object using the supplied credentials according to Poloniex's requirements.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """
        payload = request_obj.get_data().copy()
        payload.update({
            'nonce': self.nonce(),
        })

        encoded_payload = urllib.parse.urlencode(payload).encode('utf8')

        h = hmac.new(credentials['secret'].encode('utf8'), encoded_payload, hashlib.sha512)
        signature = h.hexdigest()

        headers = {
            'Key': credentials['key'],
            'Sign': signature,
        }
        request_obj.set_headers(headers)
        request_obj.set_data(payload)

    #
    # Public Endpoints
    #

    def return_ticker(self):
        """
        Returns the ticker for all markets.
        """

        response = self.query(
            method='GET',
            endpoint='public',
            params={
                'command': 'returnTicker',
            },
        )

        return response

    def return_24_volume(self):
        """
        Returns the 24-hour volume for all markets, plus totals for primary currencies.
        """
        pass

    def return_order_book(self):
        """
        Returns the order book for a given market, as well as a sequence number for use with the Push API and an
        indicator specifying whether the market is frozen. You may set currencyPair to "all" to get the order books of
        all markets.
        """
        pass

    def return_trade_history(self):
        """
        Returns the past 200 trades for a given market, or up to 50,000 trades between a range specified in UNIX
        timestamps by the "start" and "end" GET parameters.
        """
        pass

    def return_chart_data(self):
        """
        Returns candlestick chart data. Required GET parameters are "currencyPair", "period" (candlestick period in
        seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400), "start", and "end". "Start" and "end" are
        given in UNIX timestamp format and used to specify the date range for the data returned.
        """
        pass

    def return_currencies(self):
        """
        Returns information about currencies.
        """
        pass

    def return_loan_orders(self):
        """
        Returns the list of loan offers and demands for a given currency, specified by the "currency" GET
        parameter.
        """
        pass

    #
    # Authenticated Endpoints
    #

    def return_balances(self, credentials=None):
        """
        Returns all of your available balances.

        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='tradingApi',
            data={
                'command': 'returnBalances',
            },
            credentials=credentials,
        )

        return response

    def return_complete_balances(self, account='all', credentials=None):
        """
        Returns all of your balances, including available balance, balance on orders, and the estimated BTC value of
        your balance. By default, this call is limited to your exchange account; set the "account" POST parameter to
        "all" to include your margin and lending accounts.
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='tradingApi',
            data={
                'command': 'returnCompleteBalances',
                'account': account,
            },
            credentials=credentials,
        )

        return response

    def return_deposit_addresses(self):
        """
        Returns all of your deposit addresses.
        """
        pass

    def generate_new_address(self):
        """
        Generates a new deposit address for the currency specified by the "currency" POST parameter.
        """
        pass

    def return_deposits_withdrawals(self):
        """
        Returns your deposit and withdrawal history within a range, specified by the "start" and "end" POST
        parameters, both of which should be given as UNIX timestamps.
        """
        pass

    def return_open_orders(self):
        """
        Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP".
        Set "currencyPair" to "all" to return open orders for all markets.
        """
        pass

    def return_trade_history_(self):
        """
        Returns your trade history for a given market, specified by the "currencyPair" POST parameter. You may
        specify "all" as the currencyPair to receive your trade history for all markets. You may optionally specify a
        range via "start" and/or "end" POST parameters, given in UNIX timestamp format; if you do not specify a range,
        it will be limited to one day. You may optionally limit the number of entries returned using the "limit"
        parameter, up to a maximum of 10,000. If the "limit" parameter is not specified, no more than 500 entries will
        be returned.
        """
        pass

    def return_order_trades(self):
        """
        Returns all trades involving a given order, specified by the "orderNumber" POST parameter. If no trades for
        the order have occurred or you specify an order that does not belong to you, you will receive an error.
        """
        pass

    def buy(self):
        """
        Places a limit buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        If successful, the method will return the order number.

        You may optionally set "fillOrKill", "immediateOrCancel", "postOnly" to 1. A fill-or-kill order will either fill
        in its entirety or be completely aborted. An immediate-or-cancel order can be partially or completely filled,
        but any portion of the order that cannot be filled immediately will be canceled rather than left on the order
        book. A post-only order will only be placed if no portion of it fills immediately; this guarantees you will
        never pay the taker fee on any part of the order that fills.
        """
        pass

    def sell(self):
        """
        Places a sell order in a given market. Parameters and output are the same as for the buy method.
        """
        pass

    def cancel_order(self):
        """
        Cancels an order you have placed in a given market. Required POST parameter is "orderNumber".
        """
        pass

    def move_order(self):
        """
        Cancels an order and places a new one of the same type in a single atomic transaction, meaning either both
        operations will succeed or both will fail. Required POST parameters are "orderNumber" and "rate"; you may
        optionally specify "amount" if you wish to change the amount of the new order. "postOnly" or "immediateOrCancel"
        may be specified for exchange orders, but will have no effect on margin orders.
        """
        pass

    def withdraw(self):
        """
        Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method,
        the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount",
        and "address". For XMR withdrawals, you may optionally specify "paymentId".
        """
        pass

    def return_fee_info(self):
        """
        If you are enrolled in the maker-taker fee schedule, returns your current trading fees and trailing 30-day
        volume in BTC. This information is updated once every 24 hours.
        """
        pass

    def return_available_account_balances(self):
        """
        Returns your balances sorted by account. You may optionally specify the "account" POST parameter if you wish to
        fetch only the balances of one account. Please note that balances in your margin account may not be accessible
        if you have any open margin positions or orders.
        """
        pass

    def return_tradable_balances(self):
        """
        Returns your current tradable balances for each currency in each market for which margin trading is enabled.
        Please note that these balances may vary continually with market conditions.
        """
        pass

    def transfer_balance(self):
        """
        Transfers funds from one account to another (e.g. from your exchange account to your margin account). Required
        POST parameters are "currency", "amount", "fromAccount", and "toAccount".
        """
        pass

    def return_margin_account_summary(self):
        """
        Returns a summary of your entire margin account. This is the same information you will find in the Margin
        Account section of the Margin Trading page, under the Markets list.
        """
        pass

    def margin_buy(self):
        """
        Places a margin buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        You may optionally specify a maximum lending rate using the "lendingRate" parameter. If successful, the method
        will return the order number and any trades immediately resulting from your order.
        """
        pass

    def margin_sell(self):
        """
        Places a margin sell order in a given market. Parameters and output are the same as for the marginBuy method.
        """
        pass

    def get_margin_position(self):
        """
        Returns information about your margin position in a given market, specified by the "currencyPair" POST
        parameter. You may set "currencyPair" to "all" if you wish to fetch all of your margin positions at once. If you
        have no margin position in the specified market, "type" will be set to "none". "liquidationPrice" is an
        estimate, and does not necessarily represent the price at which an actual forced liquidation will occur. If you
        have no liquidation price, the value will be -1.
        """
        pass

    def close_margin_position(self):
        """
        Closes your margin position in a given market (specified by the "currencyPair" POST parameter) using a market
        order. This call will also return success if you do not have an open position in the specified market.
        """
        pass

    def create_loan_offer(self):
        """
        Creates a loan offer for a given currency. Required POST parameters are "currency", "amount", "duration",
        "autoRenew" (0 or 1), and "lendingRate".
        """
        pass

    def cancel_loan_offer(self):
        """
        Cancels a loan offer specified by the "orderNumber" POST parameter.
        """
        pass

    def return_open_loan_offers(self):
        """
        Returns your open loan offers for each currency.
        """
        pass

    def return_active_loans(self):
        """
        Returns your active loans for each currency.
        """
        pass

    def return_lending_history(self):
        """
        Returns your lending history within a time range specified by the "start" and "end" POST parameters as UNIX
        timestamps. "limit" may also be specified to limit the number of rows returned.
        """
        pass

    def toggle_auto_renew(self):
        """
        Toggles the autoRenew setting on an active loan, specified by the "orderNumber" POST parameter. If successful,
        "message" will indicate the new autoRenew setting.
        """
        pass
