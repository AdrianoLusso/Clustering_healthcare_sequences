from abc import ABC,abstractmethod
from src.utils.Package import Package
from io import StringIO

class MLAlgorithm(ABC):
    """
    Represents and interface for other ML algorithms classes.

    Attributes:
        datasets (dict[str,StringIO]): datasets that works as input for the algorithm.
        hyperparameters (dict[str,...]): the algorithm hyperparameters.
    """

    def __init__(self) -> None:
        super().__init__()
        self.datasets = Package()
        self.hyperparameters = Package()

    def upload_datasets(self,input_files:dict[str,StringIO]) -> None:
        self.datasets.fit(input_files)

    def define_hyperparameters(self,params_dict:dict[str,...]) -> None:
        self.hyperparameters.fit(params_dict)

    @abstractmethod
    def apply_ML(self) -> None:
        """ Applies the ML algorithm """
        pass

    @abstractmethod
    def get_results(self)-> None:
        pass

