class CompilationError(Exception):
    """Exception raised for errors compiling a jack file

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message