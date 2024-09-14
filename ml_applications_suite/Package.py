from typing import Dict


class Package(Dict):
    
    
    def __init__(self,*args, props:Dict[str,type], **kwargs):
        super().__init__(*args, **kwargs)
        self.props = props

    def fit(self,dict:Dict):
        
        assert list(dict.keys()) == list(self.props.keys()), "The dictionary doesn't has the expected key names"

        for key in self.props.keys():
            assert type(dict[key]) == self.props[key] , "Type of key "+key+" doesn't match with "+str(self.props[key])

        self.clear()
        self.update(dict)

    def __setitem__(self, clave, valor):
        """Redefine la asignación de valores usando la notación de corchetes."""
        print(f"Asignando el valor '{valor}' a la clave '{clave}'")
        raise ValueError("Not supported for packages. Use fit() for adding all the elements at the same time.")


    
    