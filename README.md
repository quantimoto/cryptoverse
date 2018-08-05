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

To run tests development installation:
```bash
$ pytest
```

## Quickstart

Using public methods:
```python
>>> from cryptoverse import exchanges
>>> exchanges.bitfinex.ticker('LTC/BTC')
Ticker(exchange=Bitfinex, pair='LTC/BTC')
>>> exchanges.poloniex.ticker('LTC/BTC')
Ticker(exchange=Poloniex, pair='LTC/BTC')
>>> exchanges.Poloniex.ticker('LTC/BTC')
Ticker(exchange=Bitfinex, pair='LTC/BTC')
```

Using authenticated methods:
```python
>>> from cryptoverse import exchanges
>>> from cryptoverse.domain import Account, Credentials
>>> my_credentials = Credentials(key='your_key_here', secret='your_key_here')
>>> my_account = Account(exchange=exchanges.bitfinex, credentials=my_credentials, label='your_label_here')
>>> my_account
Account(exchange=Bitfinex, key='asd..', secret='qwe..', label='trading account')
>>> my_account.orders()
Orders()
```
