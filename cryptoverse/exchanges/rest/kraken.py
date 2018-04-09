import time

from ...base.rest import RESTClient


class KrakenREST(RESTClient):
    # https://www.kraken.com/help/api
    """
    Complete implementation of the Kraken REST-api as documented at:
    https://www.kraken.com/help/api
    """
    url_structure = '{base_url}/{version}/{endpoint}'
    base_url = 'https://api.kraken.com'

    # Authentication methods

    @staticmethod
    def nonce():
        return int(time.time() * 1000)

    def get_headers(self, credentials, payload):
        payload = urllib.urlencode(payload)
        headers = {
            'API-Key': credentials['key'],
            'API-Sign': self.get_signature(credentials, payload)
        }
        return headers

    def get_payload(self, params):
        payload = {
            'nonce': self.nonce(),
        }
        payload.update(params)
        return payload

    def get_signature(self, credentials, payload):
        payload = urllib.urlencode(payload)
        message = urlpath + hashlib.sha256(str(payload['nonce']) + payload).digest()
        m = hmac.new(base64.b64decode(credentials['secret']), message, hashlib.sha512)
        signature = m.hexdigest()
        return signature

    #
    # Public Endpoints
    #

    #
    # Authenticated Endpoints
    #
