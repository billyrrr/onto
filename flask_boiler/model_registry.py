"""
Ref: https://github.com/faif/python-patterns/blob/master/patterns/behavioral/registry__py3.py
"""
from collections import defaultdict


class ModelRegistry(type):
    """

    TODO: add exception handling when resolving classes
            that are destructed.

    Attributes:
    ===================
    _REGISTRY: dict
        key: name of the class
        value: class

    """

    _REGISTRY = {}
    _tree = defaultdict(set)
    _tree_r = defaultdict(set)

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        if new_cls.__name__ in mcs._REGISTRY:
            raise ValueError(
                "Class with name {} is declared more than once. "
                .format(new_cls.__name__)
            )
        mcs._REGISTRY[new_cls.__name__] = new_cls

        for base in bases:
            if issubclass(type(base), ModelRegistry):
                mcs._tree[base.__name__].add(new_cls.__name__)
                mcs._tree_r[new_cls.__name__].add(base.__name__)

        return new_cls

    @classmethod
    def get_registry(mcs):
        return dict(mcs._REGISTRY)

    @classmethod
    def _get_children_str(mcs, cls_name):
        return mcs._tree[cls_name].copy()

    @classmethod
    def _get_parents_str(mcs, cls_name):
        return mcs._tree_r[cls_name].copy()

    @classmethod
    def get_cls_from_name(mcs, obj_type_str):
        """ Returns cls from obj_type (classname string)
        obj_type must be a subclass of cls in current class/object
        """
        if obj_type_str in mcs._REGISTRY:
            return mcs._REGISTRY[obj_type_str]
        else:
            return None


class BaseRegisteredModel(metaclass=ModelRegistry):

    @classmethod
    def _get_children(cls):
        return {cls.get_cls_from_name(c_str)
                for c_str in cls._get_children_str(cls.__name__)}

    @classmethod
    def _get_subclasses(cls):
        res = {cls, }
        children = cls._get_children()
        for child in children:
            res |= child._get_subclasses()
        return res

    @classmethod
    def _get_subclasses_str(cls):
        return list(
            sorted(_cls.__name__ for _cls in cls._get_subclasses())
        )

    @classmethod
    def _get_parents(cls):
        return {cls.get_cls_from_name(c_str)
                for c_str in cls._get_parents_str(cls.__name__)}
