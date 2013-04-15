class WrongFileFormatError(Exception):
    """Raised when there's something wrong with the input file, most
    likely that it's not an OBJ.
    """
    pass

class IncompatibleMatricesError(Exception):
    """Raised in case we're trying to perform an operation on matrices
    that is not defined (for example, adding two matrices whose
    dimensions don't match).
    """
    pass
