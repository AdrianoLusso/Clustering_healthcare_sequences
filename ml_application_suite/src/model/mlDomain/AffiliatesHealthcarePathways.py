from .MLDomain import MLDomain
from io import StringIO

class AffiliatesHealthcarePathways(MLDomain):
    """
    A domain for the healthcare pathways of the healthcare's affiliates. A pathway is a sequence of timeframes, where each timeframe has a state that represent the health situation of a particular affiliate.

    Attributes:
        timeframe_spanish_to_english (dict[str,str]): makes a translation from a timeframe input by the user (in spanish) to the language used for this class (in english).
        timeframe_english_to_pandas (dict[str,str]):  makes a translation from a timeframe in english into the pandas timeframe code.
        timeframe_unity (str): the unity size of a timeframe. It could be 'anio', 'semestre' or 'mes'.
        n_timeframes (int): number of timeframes per pathway.
    """

    timeframe_spanish_to_english:dict[str,str] = {
        'anio':'year',
        'semestre':'semester',
        'mes':'month'
    }
    timeframe_english_to_pandas = {
        'year':'YE',
        'semester':'6ME',
        'month':'ME'
    }

    def __init__(self,datasets:dict[str,StringIO], timeframe_unity:str ,n_timeframes:int) -> None:
        """
        Args:
             datasets (dict[str,StringIO]): datasets that forms the domain.
             timeframe_unity (str): the unity size of a timeframe. It could be 'anio', 'semestre' or 'mes'.
             n_timeframes (int): number of timeframes per pathway.
        """
        super().__init__(datasets)
        self.timeframe_unity: str = timeframe_unity
        self.n_timeframes: int = n_timeframes

