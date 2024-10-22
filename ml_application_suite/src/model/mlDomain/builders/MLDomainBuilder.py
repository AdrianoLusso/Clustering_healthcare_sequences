from abc import ABC
from io import StringIO

class MLDomainBuilder(ABC):
    """
    Represents an interface for builders of ML domains. An ML domain builder is encharged of executing different combinations of building steps, in order to get a final ML domain product.

    Attributes:
        debug (bool): if True, makes some prints for debugging purposes.
    """

    def __init__(self,debug:bool) -> None:
        """
        Parameters:
            debug (bool): if True, makes some prints for debugging purposes.
        """
        super().__init__()
        self.debug = debug
