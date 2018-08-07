from ..rest import Bl3pREST
from ...base.interface import ExchangeInterface


class Bl3pInterface(ExchangeInterface):
    slug = 'bl3p'

    def __init__(self):
        self.rest_client = Bl3pREST()
