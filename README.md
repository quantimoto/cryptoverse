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

After you store your keys in ~/.cryptoverse/default.kdbx, you can use authenticated methods:
```python
>>> cryptoverse.load_accounts()
Password: ***

>>> myaccount = cryptoverse.accounts['bitfinex account1']
>>> myaccount
Account(exchange=Bitfinex(), credentials=Credentials(key='abc..123', secret='qwe..890'), label='account1')

>>> myaccount.wallets('exchange')
ExchangeWallet(label=exchange):
Balances():
	Balance(instrument=Instrument('BTC'), amount=..., available=...),
	Balance(instrument=Instrument('USD'), amount=..., available=...),

>>> myaccount.orders()
Orders():
    Order(pair=Pair('BTC/USD'), side='...', amount=..., price=..., fee_percentage=0.1, status='active')

>>> myorder = myaccount.create_order('BTC/USD', 'buy', input='100%', price='bid')
>>> myorder
Order(pair=Pair('BTC/USD'), side='buy', amount=..., price=..., fee_percentage=0.1)

>>> myorder.place()
Order(pair=Pair('BTC/USD'), side='buy', amount=..., price=..., fee_percentage=0.1, status='active')

>>> myaccount.orders()
Orders():
    Order(pair=Pair('BTC/USD'), side='buy', amount=..., price=..., fee_percentage=0.1, status='active')

>>> myorder.cancel()
Order(pair=Pair('BTC/USD'), side='buy', amount=..., price=..., fee_percentage=0.1, status='cancelled')
```
