class VmWriterError(Exception):
    """Exception raised for errors related to the VmWriter module.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message