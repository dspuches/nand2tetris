class TokenizerError(Exception):
    """Exception raised for errors tokenizing a line.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message