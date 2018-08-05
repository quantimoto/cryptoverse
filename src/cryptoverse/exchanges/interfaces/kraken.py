from ..rest import KrakenREST
from ...base.interface import ExchangeInterface


class KrakenInterface(ExchangeInterface):
    slug = 'kraken'

    def __init__(self):
        self.rest_client = KrakenREST()
