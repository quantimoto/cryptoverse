#### *** This repository is currently in planning stage. ***

# cryptoverse
Cryptocurrency focused quantitative finance tools.


## Install

To install with pip, open a terminal and enter:
```bash
$ pip install cryptoverse
```

If you want to install the sources for development:
```bash
$ git clone https://github.com/quantimoto/cryptoverse
$ cd cryptoverse
$ pip install -r requirements.txt
$ pip install -e .
```

To run tests:
```bash
$ pytest
```

## Quickstart

Load the module
```python
>>> import cryptoverse
```

Using public methods:
```python
>>> cryptoverse.exchanges.bitfinex.ticker('LTC/BTC')
Ticker(exchange=Bitfinex(), pair='LTC/BTC')

>>> cryptoverse.exchanges.poloniex.ticker('LTC/BTC')
Ticker(exchange=Poloniex(), pair='LTC/BTC')

>>> cryptoverse.exchanges.kraken.ticker('LTC/BTC')
Ticker(exchange=Kraken(), pair='LTC/BTC')
```

When you store your keys in ~/.cryptoverse/default.kdbx, you can use authenticated methods:
```python
>>> cryptoverse.load_accounts()
Password: ***
>>> cryptoverse.accounts['bitfinex account1'].balances()
>>> account = cryptoverse.accounts.bitfinex_account1
>>> account
Account(exchange=Bitfinex(), credentials=Credentials(key='abc..123', secret='qwe..890'), label='account1')
>>> account.balances()
>>> account.orders()

>>> order = account.create_order('BTC/USD', 'buy', amount=0.1, price=1000)
>>> order
Order(pair=Pair('BTC/USD'), side='buy', amount=0.1, price=1000, fee_percentage=0.1)
>>> order.place()
Order(pair=Pair('BTC/USD'), side='buy', amount=0.1, price=1000, fee_percentage=0.1, status='active')
>>> account.orders()
Orders():
    Order(pair=Pair('BTC/USD'), side='buy', amount=0.1, price=1000, fee_percentage=0.1, status='active')
>>> order.cancel()
Order(pair=Pair('BTC/USD'), side='buy', amount=0.1, price=1000, fee_percentage=0.1, status='cancelled')
```
