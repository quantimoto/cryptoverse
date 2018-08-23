class MissingCredentialsException(UserWarning):
    """
    Raised when authentication credentials have not been supplied.
    """
    pass


class ExchangeDecodeException(BaseException):
    pass


class ExchangeRateLimitException(BaseException):
    pass


class ExchangeException(BaseException):
    pass
