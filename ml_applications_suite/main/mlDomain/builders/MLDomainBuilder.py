from abc import ABC

class MLDomainBuilder(ABC):

    def __init__(self,debug) -> None:
        super().__init__()
        self.debug = debug
        product = None

