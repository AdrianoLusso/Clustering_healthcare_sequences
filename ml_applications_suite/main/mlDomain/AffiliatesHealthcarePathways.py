from .MLDomain import MLDomain

class AffiliatesHealthcarePathways(MLDomain):

    timeframes_spanish_to_english = {
        'anio':'year',
        'semestre':'semester',
        'mes':'month'
    }
    timeframe_english_to_pandas = {
        'year':'YE',
        'semester':'6ME',
        'month':'ME'
    }

    def __init__(self,directories, timeframe_unity,n_timeframes) -> None:
        super().__init__(directories)
        self.timeframe_unity = timeframe_unity
        self.n_timeframes = n_timeframes

