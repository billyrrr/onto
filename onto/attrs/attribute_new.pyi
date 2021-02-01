from typing import TypeVar, Generic, Type, Optional, Union, overload

T = TypeVar('T')
V = TypeVar('V')

class AttributeBase(Generic[T, V]):

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> AttributeBase:
        ...

    @overload
    def __get__(self, instance: T, owner: Type[T]) -> V:
        ...  # noqa: F811

    @property
    def optional(self) -> AttributeBase: ...

    def of_type(self, type_cls: V):
        return self

    @property
    def string(self: T):
        return self.of_type(str)

    # def __init__(self, getter: Callable[[Type[T]], V]) -> None:
    #     self.getter = getter

    # def __get__(self, instance: S, owner: typing.Type[S]) -> T: ...

    # str = string

    # def __get__(self, instance: None, owner: typing.Type[T]) -> attrs: ...

    # @overload
    # def __get__(self, instance: T, owner: typing.Type[T]) -> S: ...  # noqa: F811

    # def __get__(self, instance: Optional[S], owner: typing.Type[S]) -> T: ...

