from flask_boiler import fields
from typing import Type, Generic, TypeVar, Optional


class ValueNotProvided:
    pass


class _NA:
    pass


T = TypeVar("T")


class AttributeBase(Generic[T]):

    field_cls: Type[fields.Field] = None

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        return fields.Field()

    def __set_name__(self, owner, name):
        self.parent = owner
        self.name = name

    def __get__(self, instance, owner):
        """ Only allow attribute object to be invoked "get" on
                a class, and not an instance.

        :param instance:
        :param owner:
        :return:
        """
        if instance is None:
            return self
        else:
            raise AttributeError()

    def __init__(
            self,
            # *,
            # initialize,
            # initialize_value,
            # data_key,
            #
            # import_enabled,
            # import_default,
            # import_required,
            #
            # export_enabled,
            # export_default,
            # export_required,
            #
            # type_cls: Optional[Type[T]],

    ):
        """

        :param initialize: If true, initialize the value as the first step.
            The value may be set again later in the process of calling "new".
        :param initialize_value: The value to initialize the attribute to.
            May be a callable to avoid mutable default arguments.
        :param data_key: Sets import_from and export_to (field name in a
            document in the database)

        :param import_enabled: If true, the value will be imported
            to the object
        :param import_default: Import this value if the field
            name is missing from a document in the database
        :param import_required:

        :param export_enabled: If true, the value will be exported to
            a field in the database
        :param export_default: Export this value if attribute
            is missing from the object
        :param export_required:

        """
        # self._field = self.field_cls(
        #     # missing=value_if_not_loaded
        # )

        # To be set by __set_name__ when attribute instance is binded
        #   to a class
        self.parent = _NA
        self.name = _NA


class Boolean(AttributeBase):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """
    pass

    # def __init__(
    #         self,
    #         *,
    #         initialize,
    #         initialize_value,
    #         data_key,
    #
    #         import_enabled,
    #         import_default,
    #         import_required,
    #
    #         export_enabled,
    #         export_default,
    #         export_required,
    #
    #         type_cls: Optional[Type[T]],):
    #
    #     res = dict()
    #
    #     res["import_only"], res["export_only"] = \
    #         import_enabled and not export_enabled, \
    #         export_enabled and not import_enabled
    #
    #     if import_enabled:
    #         res["required"] = import_required
    #
    #     super().__init__(
    #
    #         value_if_not_loaded=value_if_not_loaded,
    #         nullable=True,
    #         *args,
    #         **kwargs
    #     )
    #
    # def __get__(self, instance, owner) -> bool:
    #     return super().__get__(instance, owner)


