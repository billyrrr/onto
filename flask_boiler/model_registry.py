"""
Ref: https://github.com/faif/python-patterns/blob/master/patterns/behavioral/registry__py3.py
"""


class ModelRegistry(type):
    """
    Attributes:
    ===================
    _REGISTRY: dict
        key: name of the class
        value: class

    """

    _REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls._REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        return dict(cls._REGISTRY)

    @classmethod
    def get_subclass_cls(cls, obj_type):
        """ Returns cls from obj_type (classname string)
        obj_type must be a subclass of cls in current class/object
        """
        if obj_type in cls._REGISTRY:
            return cls._REGISTRY[obj_type]
        else:
            return None


class BaseRegisteredModel(metaclass=ModelRegistry):
    pass

