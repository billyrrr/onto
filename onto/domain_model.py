from typing import Type

from onto.primary_object import PrimaryObject


class RemoteProxyMixin:

    from typing import TypeVar
    OriginalCls = TypeVar('OriginalCls')

    _target_typename = None

    @classmethod
    def _get_cmd_topic(cls):
        from onto.name_formatter import name_formatter
        from inflection import dasherize, underscore
        name = dasherize(underscore(cls.__name__))
        return name_formatter(
            name=name,
            typ='cmd'
        )

    @classmethod
    def _get_statefun_typename(cls):
        from onto.name_formatter import ENVIRONMENT
        return getattr(cls, 'statefun_typename', f'{ENVIRONMENT}/{cls.__name__}')

    @classmethod
    def method_proxy(cls: Type[OriginalCls], doc_id: str, topic=None) -> OriginalCls:
        from onto.stateful_functions import StatefunProxy
        obj = StatefunProxy(
            wrapped=cls,
            target_id=doc_id,
            invocation_type='Method',
            topic=topic or cls._get_cmd_topic(),
            target_typename=cls._get_target_typename(),
        )
        return obj

    @classmethod
    def _get_target_typename(cls):
        """
        Stateful Functions typename
        eg. example/Foo

        """
        if cls._target_typename is None:
            return f'example/{cls.__name__}'
        else:
            return cls._target_typename

    @classmethod
    def initializer_proxy(cls: Type[OriginalCls], doc_id: str, topic=None) -> Type[OriginalCls]:
        from onto.stateful_functions import StatefunProxy
        obj = StatefunProxy(
            wrapped=cls,
            target_id=doc_id,
            invocation_type='ClassMethod',
            topic=topic or cls._get_cmd_topic(),
            target_typename=cls._get_target_typename(),
        )
        return obj


class DomainModel(PrimaryObject, RemoteProxyMixin):
    """
    Domain model is intended for handling business logic.
    """

    @classmethod
    def _datastore(cls):
        from onto.context import Context as CTX
        return CTX.db



