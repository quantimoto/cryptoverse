from ..rest import PoloniexREST
from ...base.interface import ExchangeInterface


class PoloniexInterface(ExchangeInterface):
    slug = 'poloniex'

    def __init__(self):
        self.rest_client = PoloniexREST()
