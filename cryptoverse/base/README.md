RESTClient

The RESTClient is a general rest-client used as a base class for the exchanges, block-explorers and other api-providers.

Features:
- Automatic retry on specific failures.
    - Retry on rate-limit error with dynamic delay
    - Retry on invalid nonce
- Uses response object, that contains all context of the request and every abstraction of the response data.
- Keeps log of requests and their responses code/status
