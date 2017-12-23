#### *** This repository is currently in planning stage. ***

# cryptoverse
Cryptocurrency focused quantitative finance tools.


## Install

Install with pip
```bash
$ pip install cryptoverse
```

## Quickstart
```python
>>> from cryptoverse import exchanges
>>> print(exchanges.bitfinex.ticker('LTC/BTC'))
>>> print(exchanges.poloniex.ticker('LTC/BTC'))
>>> print(exchanges.kraken.ticker('LTC/BTC'))
```
