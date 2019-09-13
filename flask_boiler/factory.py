from typing import Union

from flask_boiler.model_registry import BaseRegisteredModel
from flask_boiler.serializable import T, Schemed, AutoInitialized, NewMixin, \
    Importable, Exportable, U, Serializable


class ClsFactory:

    @classmethod
    def create_from_root(
            cls, name, schema: T,
            root_cls=None,
            additional_base_tuple=None):
        pass

    @classmethod
    def create_customized(
            cls, name, schema: T,
            auto_initialized=True,
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

        if auto_initialized:
            base_list.append(AutoInitialized)
        else:
            base_list.append(NewMixin)

        if importable:
            base_list.append(Importable)

        if exportable:
            base_list.append(Exportable)

        return cls.create(
            name=name,
            schema=schema,
            base_tuple=tuple(base_list)
        )

    @classmethod
    def create(cls, name, schema: T,
               base:U=Serializable,
               base_tuple=None) -> Union[T, U]:

        existing = BaseRegisteredModel.get_cls_from_name(name)
        if existing is None:
            new_cls = type(name,  # class name
                           base_tuple or (base, ),
                           dict(
                               _schema_cls=schema
                           )
                           )
            return new_cls
        else:
            return existing
