class SymbolTableError(Exception):
    """Exception raised for errors with the symbol table.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message