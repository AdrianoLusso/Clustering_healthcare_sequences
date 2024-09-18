from abc import ABC,abstractmethod
from ..utils.Package import Package

class MLAlgorithm(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.datasets = Package()
        self.hyperparameters = Package()

    def upload_datasets(self,input_directories:dict):
        self.datasets.fit(input_directories)

    def define_hyperparameters(self,params_dict:dict):
        self.hyperparameters.fit(params_dict)

    @abstractmethod
    def apply_ML(self):
        pass

    @abstractmethod
    def get_results(self):
        pass

