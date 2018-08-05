# Exchanges

This is the folder to place the exchange api modules

API's should be implemented in the following way:

Layer 1
- rest
    One-to-one translation from the exchange rest api to python methods

Layer 2
- cache all the data in a database, wether in memory, disk or remote server.
    This is important because differences between the exchange data can not always be receives in the the same manner.
    For example: caching all data prevents spamming the exchange, where we're iterating through markets when some exchanges allow calls that return multiple records.
    Also the user should not have to worry about spamming the exchange. The cache layers caches data that might get requests more often than the exchanges rate_limit allows.

Layer 3
- interfaces
    This is the api that the user should use. The interface gets all data from the cache layer, but also makes sure it's getting refreshed when required.
