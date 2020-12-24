class SyntaxError(Exception):
    """Exception raised for errors compiling a jack file

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, tkn, message):
        self.message = message
        self.line_num = tkn._line_count