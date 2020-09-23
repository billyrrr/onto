from typing import TypeVar, Type, Union

from onto.models.base import BaseRegisteredModel, Serializable, Schemed
from onto.models.mixin import Importable, Exportable, NewMixin

T = TypeVar('T')
U = TypeVar('U')


class ClsFactory:

    @classmethod
    def create_from_root(
            cls, name, schema,
            root_cls=None,
            additional_base_tuple=None):
        pass

    @classmethod
    def create_customized(
            cls, name, schema,
            importable=True,
            exportable=True):
        """

        :param name: name of the new class
        :param schema: schema of the new class
        :param auto_initialized: If set to True, the instance variables
                will be initialized to the default value read from
                the corresponding field.
        :param importable: If set to True, the instance variables can
                be set in batch from dictionary.
        :param exportable: If set to True, the object can be exported
                to a dictionary.
        :return:
        """
        base_list = [BaseRegisteredModel, Schemed]

        if importable:
            base_list.append(Importable)

        if exportable:
            base_list.append(Exportable)

        base_list.append(NewMixin)

        return cls.create(
            name=name,
            schema=schema,
            base_tuple=tuple(base_list)
        )

    @classmethod
    def create(cls, name, schema: Type[T],
               base: Type[U] = Serializable,
               base_tuple=None) -> Union[Type[U], Type[T]]:

        existing = BaseRegisteredModel.get_cls_from_name(name)
        if existing is None:
            new_cls = type(name,  # class name
                           base_tuple or (base, ),
                           dict(
                               _schema_cls=schema,
                           )
                           )
            return new_cls
        else:
            return existing
