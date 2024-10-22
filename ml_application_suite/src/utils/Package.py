from typing import Dict,Callable,get_args


class Package(Dict):
    """
    Dictionary subclass for restricting its elements by a set of types and constraints.

    Attributes:
        types (dict[str,type]): a dict formed by tuples (k,t) that restricts the types of the package elements. For each tuple, the element with key 'k' must be of the type marked by t'.
        constraints (dict[str,Callable[...,bool]]): a dict formed by tuples (k,c) that add a set of constraints to the package elements. For each tuple, the element with key 'k' must comply the set of restrictions 'c'.

    Example:
        p = Package(
                types={
                    'prop1': Union[int,str],
                    'prop2': Union[float,None]
                },
                constraints={
                    'prop1': lambda x: (x == 'automatic' or x > 1),
                    'prop2': lambda x: (x is None or -1 < x < 1)
                }
        )
    """
    
    def __init__(self,*args, types:dict[str,type]={}, constraints:dict[str,Callable[..., bool]]={} , **kwargs) -> None:
        """
        Args:
            types (dict[str,type]): a dict formed by tuples (k,t) that restricts the types of the package elements. For each tuple, the element with key 'k' must be of the type marked by t'.
            constraints (dict[str,Callable[...,bool]]): a dict formed by tuples (k,c) that add a set of constraints to the package elements. For each tuple, the element with key 'k' must comply the set of restrictions 'c'.
        """
        super().__init__(*args, **kwargs)

        assert (
            constraints == {}
            or list(types.keys()) == list(constraints.keys())
            ), "The set of keys of the types and of the constraints must be the same"

        self.types = types
        self.constraints = constraints
    def __setitem__(self, clave, valor) -> None:
        """
        Redefines the value assignation used by [] notation.
        """
        raise ValueError("Not supported for packages. Use fit() for adding all the elements at the same time.")

    def fit(self, dictionary:dict) -> None:
        """
        Fits a dictionary into the package, making it comply the types and constraints expected.

        Args:
            dictionary (dict): the dictionary to fit.
        """
        assert list(dictionary.keys()) == list(self.types.keys()), "The dictionary doesn't has the expected key names"

        for key in self.types.keys():
            assert self.__check_type(dictionary[key], self.types[key]), "Type of key " + key + " doesn't match with " + str(self.types[key])

        if self.constraints != {}:
            for key,value in self.constraints.items():
                assert (
                    value is None
                    or value(dictionary[key])
                    ),'Constraint for key '+key+' was broken'

        # If the types and constraints are complied, the dictionary is saved as the package.
        self.clear()
        self.update(dictionary)

    @staticmethod
    def __check_type(param,types) -> bool:
        """
        Checks if the type of the parameter is valid.

        Args:
            param: the parameter to check the type of.
            types: a type, or union of types, used for the check.

        Returns: True if the type is valid, otherwise False.
        """

        # if types is an union of types, it will return them in a tuple
        union_types_container = get_args(types)
        if union_types_container:
            result = isinstance(param,union_types_container)
        else:
            result = isinstance(param,types)

        return result


    
    