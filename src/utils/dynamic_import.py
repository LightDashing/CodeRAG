import importlib

def import_class(class_config: dict, BaseClass: object) -> object:
    
    module = importlib.import_module(class_config['module'])
    InitModule = getattr(module, class_config['name'])
    
    if not issubclass(InitModule, BaseClass):
                raise TypeError(f"{InitModule.__name__} is not subclass of {BaseClass.__name__}")
            
    return InitModule