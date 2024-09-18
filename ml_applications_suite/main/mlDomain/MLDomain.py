from abc import ABC

class MLDomain(ABC):

    def __init__(self,directories) -> None:
        super().__init__()
        self.datasets_directories = directories



