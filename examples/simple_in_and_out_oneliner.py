import cryptoverse

"""
This example shows two ways of writing automating a simple trade. Don't blindly run this script on your actual account.
You can use PyCharm's cell execution on the code blocks to play with this script.
"""

# %% After you've set-up the KeepassX file with your account api-keys, you can load the keys with the following command.
# ## You will be asked for your password, if you haven't set-up the KeepassX password in your environment variables.
cryptoverse.load_accounts()

# %% Using method chaining, you could do a simple in-and-out trade with one line of code:
cryptoverse.accounts['bitfinex_account1'].create_order('BTC/USD', 'sell', input='100%', price='ask') \
    .place().sleep_while_active().followup(output='+1%').place()
# very useful for typing simple strategies quickly from the interactive console
