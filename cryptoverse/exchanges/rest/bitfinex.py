from cryptoverse.base import RESTClient, ResponseObj, rate_limit


class BitfinexPublic(RESTClient):

    url = 'https://api.bitfinex.com/v1'

    @rate_limit(30, 60)
    def ticker(self, symbol):
        """
        Ticker

        The ticker is a high level overview of the state of the market. It shows you the current best bid and ask, as
        well as the last trade price. It also includes information such as daily volume and how much the price has moved
        over the last day.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        """
        raise NotImplementedError

    @rate_limit(10, 60)
    def stats(self, symbol):
        """
        Stats

        Various statistics about the requested pair.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        """
        raise NotImplementedError

    @rate_limit(45, 60)
    def fundingbook(self, currency, limit_bids=50, limit_asks=50):
        """
        Fundingbook

        Get the full margin funding book

        :param str currency:
        :param int limit_bids: Limit the number of funding bids returned. May be 0 in which case the array of bids is
            empty
        :param int limit_asks: Limit the number of funding offers returned. May be 0 in which case the array of asks is
            empty
        """
        raise NotImplementedError

    @rate_limit(60, 60)
    def orderbook(self, symbol, limit_bids=50, limit_asks=50, group=1):
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
        raise NotImplementedError

    @rate_limit(45, 60)
    def trades(self, symbol, timestamp=None, limit_trades=50):
        """
        Trades

        Get a list of the most recent trades for the given symbol.

        :param str symbol: The symbol you want information about. You can find the list of valid symbols by calling the
            symbols() endpoint.
        :param timestamp: Only show trades at or after this timestamp
        :param int limit_trades: Limit the number of trades returned. Must be >= 1
        """
        raise NotImplementedError

    @rate_limit(60, 60)
    def lends(self, currency, timestamp=None, limit_lends=50):
        """
        Lends

        Get a list of the most recent funding data for the given currency: total amount provided and Flash Return Rate
        (in % by 365 days) over time.

        :param str currency:
        :param timestamp: Only show data at or after this timestamp
        :param int limit_lends: Limit the amount of funding data returned. Must be >= 1
        """
        raise NotImplementedError

    @rate_limit(5, 60)
    def symbols(self):
        """
        Symbols

        A list of symbol names.
        """
        raise NotImplementedError

    @rate_limit(5, 60)
    def symbol_details(self):
        """
        Symbol Details

        Get a list of valid symbol IDs and the pair details.
        """
        raise NotImplementedError

    def account_infos(self):
        """
        Account Info

        Return information about your account (trading fees)
        """
        raise NotImplementedError

    def account_fees(self):
        """
        Account Fees

        See the fees applied to your withdrawals
        """
        raise NotImplementedError

    def summary(self):
        """
        Summary

        Returns a 30-day summary of your trading volume and return on margin funding.
        """
        raise NotImplementedError

    def deposit_new(self, method, wallet_name, renew=0):
        """
        Deposit

        Return your deposit address to make a new deposit.

        :param str method: Method of deposit (methods accepted: "bitcoin", "litecoin", "ethereum", "tetheruso",
            "ethereumc", "zcash", "monero", "iota", "bcash").
        :param str wallet_name: Wallet to deposit in (accepted: "trading", "exchange", "deposit"). Your wallet needs to
            already exist
        :param int renew: Default is 0. If set to 1, will return a new unused deposit address
        """
        raise NotImplementedError

    def key_info(self):
        """
        Key Permissions

        Check the permissions of the key being used to generate this request.
        """
        raise NotImplementedError

    def margin_infos(self):
        """
        Margin Information

        See your trading wallet information for margin trading.
        """
        raise NotImplementedError

    @rate_limit(20, 60)
    def balances(self):
        """
        Wallet Balances

        See your balances
        """
        raise NotImplementedError

    def transfer(self, amount, currency, walletfrom, walletto):
        """
        Transfer Between Wallets

        Allow you to move available balances between your wallets.

        :param float amount: Amount to transfer
        :param str currency: Currency of funds to transfer.
        :param str walletfrom: Wallet to transfer from. Can be "trading", "deposit" or "exchange"
        :param str walletto: Wallet to transfer to. Can be "trading", "deposit" or "exchange"
        """
        raise NotImplementedError

    def withdraw(self, withdraw_type, walletselected, amount, address, payment_id=None, account_name=None,
                 account_number=None, swift=None, bank_name=None, bank_address=None, bank_city=None, bank_country=None,
                 detail_payment=None, express_wire=None, intermediary_bank_name=None, intermediary_bank_address=None,
                 intermediary_bank_city=None, intermediary_bank_country=None, intermediary_bank_account=None,
                 intermediary_bank_swift=None):
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
        """
        raise NotImplementedError

    def order_new(self, symbol, amount, price, side, type_, exchange=None, is_hidden=None, is_postonly=None,
                  use_all_available=None, ocoorder=None, buy_price_oco=None, sell_price_oco=None):
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
        """
        raise NotImplementedError

    def order_new_multi(self, symbol, amount, price, side, type_, exchange=None):
        """
        Multiple New Orders

        Submit several new orders at once.

        :param str symbol: The name of the symbol (see symbols()).
        :param float amount: Order size: how much you want to buy or sell
        :param float price: Price to buy or sell at. Must be positive. Use random number for market orders.
        :param str side: Either "buy" or "sell".
        :param str type_: Either "market" / "limit" / "stop" / "trailing-stop" / "fill-or-kill".
        :param str exchange: "bitfinex"
        """
        raise NotImplementedError

    def order_cancel(self, order_id):
        """
        Cancel Order

        Cancel an order.

        :param int order_id: The order ID given by order_new()
        """
        raise NotImplementedError

    def order_cancel_multi(self, order_ids):
        """
        Cancel Multiple Orders

        Cancel multiples orders at once.

        :param list(int) order_ids: An array of the order IDs given by order_new() or order_new_multi().
        """
        raise NotImplementedError

    def order_cancel_all(self):
        """
        Cancel All Orders

        Cancel all active orders at once.
        """
        raise NotImplementedError

    def order_cancel_replace(self, order_id, symbol=None, amount=None, price=None, exchange=None, side=None, type_=None,
                             is_hidden=None, is_postonly=None, use_remaining=None):
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
        """
        raise NotImplementedError

    def order_status(self, order_id):
        """
        Order Status

        Get the status of an order. Is it active? Was it cancelled? To what extent has it been executed? etc.

        :param int order_id: The order ID given by order_new()
        """
        raise NotImplementedError

    def orders(self):
        """
        Active Orders

        View your active orders.
        """
        raise NotImplementedError

    @rate_limit(1, 60)
    def orders_hist(self, limit=None):
        """
        Orders History

        View your latest inactive orders.
        Limited to last 3 days and 1 request per minute.

        :param int limit: Limit number of results
        """
        raise NotImplementedError

    def positions(self):
        """
        Active Positions

        View your active positions.
        """
        raise NotImplementedError

    def positions_claim(self, position_id, amount):
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
        """
        raise NotImplementedError

    @rate_limit(20, 60)
    def history(self, currency, since=None, until=None, limit=None, wallet=None):
        """
        Balance History

        View all of your balance ledger entries.

        :param str currency: The currency to look for.
        :param since: Return only the history after this timestamp.
        :param until: Return only the history before this timestamp.
        :param int limit: Limit the number of entries to return.
        :param str wallet: Return only entries that took place in this wallet. Accepted inputs are: "trading",
            "exchange", "deposit".
        """
        raise NotImplementedError

    @rate_limit(20, 60)
    def history_movements(self, currency, method=None, since=None, until=None, limit=None):
        """
        Deposit-Withdrawal History

        View your past deposits/withdrawals.

        :param str currency: The currency to look for.
        :param str method: The method of the deposit/withdrawal (can be "bitcoin", "litecoin", "darkcoin", "wire").
        :param since: Return only the history after this timestamp.
        :param until: Return only the history before this timestamp.
        :param int limit: Limit the number of entries to return.
        """
        raise NotImplementedError

    @rate_limit(45, 60)
    def mytrades(self, symbol, timestamp=None, until=None, limit_trades=None, reverse=None):
        """
        Past Trades

        View you past trades.

        :param str symbol: The pair traded (BTCUSD, ...).
        :param timestamp: Trades made before this timestamp won't be returned.
        :param until: Trade made after this timestamp won't be returned.
        :param int limit_trades: Limit the number of trades returned.
        :param int reverse: Return trades in reverse order (the oldest comes first). Default is returning newest trades
            first.
        """
        raise NotImplementedError

    def offer_new(self, currency, amount, rate, period, direction):
        """
        New Offer

        Submit a new Offer

        :param str currency: The name of the currency.
        :param float amount: Order size: how much to lend or borrow.
        :param float rate: Rate to lend or borrow at. In percentage per 365 days. (Set to 0 for FRR).
        :param int period: Number of days of the funding contract (in days)
        :param str direction: Either "lend" or "loan".
        """
        raise NotImplementedError

    def offer_cancel(self, offer_id):
        """
        Cancel Offer

        Cancel an offer.
        
        :param int offer_id: The offer ID given by offer_new().
        """
        raise NotImplementedError

    def offer_status(self, offer_id):
        """
        Offer Status

        Get the status of an offer. Is it active? Was it cancelled? To what extent has it been executed? etc.
        
        :param int offer_id: The offer ID given by offer_new().
        """
        raise NotImplementedError

    def credits(self):
        """
        Active Credits

        View your funds currently taken (active credits).
        """
        raise NotImplementedError

    def offers(self):
        """
        Offers

        View your active offers.
        """
        raise NotImplementedError

    @rate_limit(1, 60)
    def offer_hist(self, limit=None):
        """
        Offers History

        View your latest inactive offers.
        Limited to last 3 days and 1 request per minute.
        
        :param int limit: Limit number of results
        """
        raise NotImplementedError

    @rate_limit(45, 60)
    def mytrades_funding(self, symbol, until=None, limit_trades=None):
        """
        Past Funding Trades

        View your past trades.
        
        :param str symbol: The pair traded (USD, ...).
        :param until: Trades made after this timestamp won't be returned.
        :param int limit_trades: Limit the number of trades returned.
        """
        raise NotImplementedError

    def taken_funds(self):
        """
        Active Funding Used in a margin position
        """
        raise NotImplementedError

    def unused_taken_funds(self):
        """
        Active Funding Not Used in a margin position

        View your funding currently borrowed and not used (available for a new margin position).
        """
        raise NotImplementedError

    def total_taken_funds(self):
        """
        Total Taken Funds

        View the total of your active funding used in your position(s).
        """
        raise NotImplementedError

    def funding_close(self, swap_id):
        """
        Close Margin Funding

        Allow you to close an unused or used taken fund

        :param int swap_id: The ID given by taken_funds() or unused_taken_funds()
        """
        raise NotImplementedError

    def basket_manage(self, amount=None, dir_=None, name=None):
        """
        Basket Manage

        This endpoint is used to manage the creation or destruction of tokens via splitting or merging. For the moment,
        this is only useful for the bcc and bcu tokens.

        :param str amount: The amount you wish to split or merge
        :param int dir_: 1 to split, -1 to merge
        :param str name: the symbol of the token pair you wish to create or destroy
        """
        raise NotImplementedError

    def positions_close(self, position_id):
        """
        Close Position

        Closes the selected position with a market order.

        :param int position_id: The position ID given by positions().
        """
        raise NotImplementedError
