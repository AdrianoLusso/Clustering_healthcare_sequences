from abc import ABC, abstractmethod
from typing import Dict

class MLApplication(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def preprocess_raw_dataset(self,input_directories:Dict, output_directories:Dict) -> bool:
        pass

    @abstractmethod
    def upload_preprocessed_dataset(self,input_directories:Dict) -> bool:
        pass

    @abstractmethod
    def define_hyperparameters(self,params_dict) -> bool:
        pass

    @abstractmethod
    def apply_ML(self) -> bool:
        pass

    @abstractmethod
    def get_results(self):
        pass

    @abstractmethod
    def get_results_visualizations(self):
        pass

