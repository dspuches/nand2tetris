class TokenError(Exception):
    """Exception raised for errors related to a specific token

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, token, message):
        self.token = token
        self.message = message