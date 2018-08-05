class Portfolio(object):
    """
    The 'Portfolio' object can hold exchange accounts and wallets. It's purpose is to get information on all the
    balances and values, which are spread out over multiple wallets and/or exchanges.
    """
    accounts = None
    wallets = None

    def __init__(self, accounts, wallets):
        self.set_accounts(accounts)
        self.set_wallets(wallets)

    def set_accounts(self, accounts):
        self.accounts = accounts

    def set_wallets(self, wallets):
        self.wallets = wallets
