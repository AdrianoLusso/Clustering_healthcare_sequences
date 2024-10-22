from abc import ABC
from io import StringIO

class MLDomain(ABC):
    """
    Represents an interface for other ML domain classes. An ML domain is an abstraction that models an specific area of knowledge and that can be used for ML workflows.

    Attributes:
        - datasets (dict[str,StringIO])
            directories of the datasets that forms the domain.
    """

    def __init__(self, datasets: dict[str,StringIO]) -> None:
        """
        Args:
             - datasets (dict[str,StringIO])
                datasets that forms the domain.
        """
        super().__init__()
        self.datasets = datasets
