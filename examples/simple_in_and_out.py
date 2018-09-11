import cryptoverse

"""
This example shows two ways of writing automating a simple trade. Don't blindly run this script on your actual account.
You can use PyCharm's cell execution on the code blocks to play with this script.
"""

# %% After you've set-up the KeepassX file with your account api-keys, you can load the keys with the following command.
# ## You will be asked for your password, if you haven't set-up the KeepassX password in your environment variables.
cryptoverse.load_accounts()
account = cryptoverse.accounts['bitfinex_account1']

# %% First we create an order to sell 100% of the available BTC balance at the ask price.
my_sell_order = account.create_order('BTC/USD', 'sell', input='100%', price='ask')

# %% Now we can take a look at all the calculated values. Let's print the input and output amounts
print(my_sell_order.input)
print(my_sell_order.output)
print(my_sell_order.price)

# %% When you're happy with the order we've created, uncomment and run the next line to post the order to the exchange.
# my_sell_order.place()

# %% Tell the script to block execution until the order is executed.
my_sell_order.wait_while_active()

# %% Right after the last order is executed, we calculate a followup order for +1% profit.
my_buy_order = my_sell_order.followup(output='+1%')

# %% Let's take a look at the value calculated.
print(my_buy_order.input)
print(my_buy_order.output)
print(my_buy_order.price)

# %% When you're happy with the order we've created, uncomment and run the next line to post the order to the exchange.
# my_buy_order.place()

# %% Tell the script to block execution until the order is executed.
my_buy_order.wait_while_active()

# %% We're going to block the execution again until this order is executed.
my_sell_order.wait_while_active()

# %% Now that both trades have completed we can send a notification
# notify('Trade completed. P&L +1%.')  # TODO: implement notifications


# %% Using method chaining, you could do the exact same trade from one line of code:
account.create_order('BTC/USD', 'sell', input='100%', price='ask').place().wait_for_completion().followup(
    output='+1%').place().sleep_until_filled()
# very useful for typing simple strategies quickly from the interactive console
