from typing import Dict,Callable


class Package(Dict):
    
    
    def __init__(self,*args, types:Dict[str,type]={}, constraints:Dict[str,Callable[..., bool]]={} , **kwargs):
        super().__init__(*args, **kwargs)

        assert (
            constraints == {}
            or list(types.keys()) == list(constraints.keys())
            ), "The set of keys of the types and of the constraints must be the same"

        self.types = types
        self.constraints = constraints

    def fit(self,dict:Dict):
        
        assert list(dict.keys()) == list(self.types.keys()), "The dictionary doesn't has the expected key names"

        for key in self.types.keys():
            assert type(dict[key]) == self.types[key] , "Type of key "+key+" doesn't match with "+str(self.types[key])

        if self.constraints != {}:
            for key,value in self.constraints.items():
                assert (
                    value is None
                    or value(dict[key])
                    ),'Constraint for key '+key+' was broken'

        self.clear()
        self.update(dict)

    def __setitem__(self, clave, valor):
        """Redefine la asignación de valores usando la notación de corchetes."""
        print(f"Asignando el valor '{valor}' a la clave '{clave}'")
        raise ValueError("Not supported for packages. Use fit() for adding all the elements at the same time.")

    
    