class TokenizerError(Exception):
    """Exception raised for errors tokenizing a line.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message