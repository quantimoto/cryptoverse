import base64
import hashlib
import hmac
from urllib.parse import urlencode

from ...base.rest import RESTClient
from ...exceptions import MissingCredentialsError


class KrakenREST(RESTClient):
    # https://www.kraken.com/help/api
    """
    Complete implementation of the Kraken REST-api as documented at:
    https://www.kraken.com/help/api
    """

    address = 'https://api.kraken.com'
    uri_template = '/{version}/{endpoint}'

    credentials = None

    # Authentication methods

    def sign(self, request_obj, credentials):
        # https://www.kraken.com/help/api#general-usage
        """
        Signs the request object using the supplied credentials according to Kraken's requirements.

        :param request_obj: Object containing all the attributes required to do the request.
        :param credentials: Credentials object that contains the key and secret, required to sign the request.
        """

        payload = request_obj.get_data().copy()
        payload.update({
            'nonce': self.nonce(),
        })

        encoded_payload = urlencode(payload)
        message = request_obj.get_uri().encode('utf-8') + hashlib.sha256(
            (payload['nonce'] + encoded_payload).encode('utf-8')).digest()

        h = hmac.new(
            key=base64.b64decode(credentials['secret']),
            msg=message,
            digestmod=hashlib.sha512,
        )
        signature = h.digest()

        headers = {
            'API-Key': credentials['key'],
            'API-Sign': base64.b64encode(signature).decode('utf-8'),
        }
        request_obj.set_headers(headers)
        request_obj.set_data(payload)

        return request_obj

    #
    # Public Endpoints
    #

    # @rate_limit(1, 3)  # https://www.kraken.com/help/api#api-call-rate-limit
    def time(self):
        """
        Get server time

        Result: Server's time

        unixtime =  as unix timestamp
        rfc1123 = as RFC 1123 time format
        Note: This is to aid in approximating the skew time between the server and client.
        """

        response = self.query(
            method='GET',
            endpoint='public/Time',
            path_params={
                'version': 0,
            },
        )

        return response

    def assets(self, info='info', aclass='currency', asset='all'):
        """
        Get asset info

        :param str info: info to retrieve (optional): info = all info (default)
        :param str aclass: asset class (optional): currency (default)
        :param str asset: comma delimited list of assets to get info on (optional.  default = all for given asset class)
        """

        response = self.query(
            method='GET',
            endpoint='public/Assets',
            path_params={
                'version': 0,
            },
            params={
                'info': info,
                'aclass': aclass,
                'asset': asset,
            },
        )

        return response

    def asset_pairs(self, info='info', pair='all'):
        """
        Get tradable asset pairs

        :param str info: info to retrieve (optional): info = all info (default), leverage = leverage info, fees = fees
            schedule, margin = margin info,
        :param str pair: comma delimited list of asset pairs to get info on (optional.  default = all)
        """

        response = self.query(
            method='GET',
            endpoint='public/AssetPairs',
            path_params={
                'version': 0,
            },
            params={
                'info': info,
                'pair': pair,
            },
        )

        return response

    def ticker(self):
        raise NotImplementedError

    def ohlc(self):
        raise NotImplementedError

    def depth(self):
        raise NotImplementedError

    def trades(self):
        raise NotImplementedError

    def spread(self):
        raise NotImplementedError

    #
    # Authenticated Endpoints
    #

    def trade_balance(self, aclass='currency', asset='ZUSD', credentials=None):
        """
        Get trade balance

        Result: array of trade balance info

        Note: Rates used for the floating valuation is the midpoint of the best bid and ask prices

        :param str aclass: asset class (optional): currency (default)
        :param str asset: base asset used to determine balance (default = ZUSD)
        :param dict credentials: dictionary containing authentication information like key and secret
        """

        credentials = credentials or self.credentials
        if credentials is None:
            raise MissingCredentialsError

        response = self.query(
            method='POST',
            endpoint='private/TradeBalance',
            path_params={
                'version': 0,
            },
            data={
                'aclass': aclass,
                'asset': asset,
            },
            credentials=credentials,
        )

        return response

    def open_orders(self):
        raise NotImplementedError

    def closed_orders(self):
        raise NotImplementedError

    def query_orders(self):
        raise NotImplementedError

    def trades_history(self):
        raise NotImplementedError

    def query_trades(self):
        raise NotImplementedError

    def open_positions(self):
        raise NotImplementedError

    def ledgers(self):
        raise NotImplementedError

    def query_ledgers(self):
        raise NotImplementedError

    def trade_volume(self):
        raise NotImplementedError

    def add_order(self):
        raise NotImplementedError

    def cancel_order(self):
        raise NotImplementedError

    def deposit_methods(self):
        raise NotImplementedError

    def deposit_addresses(self):
        raise NotImplementedError

    def deposit_status(self):
        raise NotImplementedError

    def withdraw_info(self):
        raise NotImplementedError

    def withdraw(self):
        raise NotImplementedError

    def withdraw_status(self):
        raise NotImplementedError

    def withdraw_cancel(self):
        raise NotImplementedError
