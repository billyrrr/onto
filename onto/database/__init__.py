import collections
import abc

from onto.common import _NA

import abc
from enum import Enum, auto


class ConditionArg(Enum):
    """
    Do not declare attributes here
    """
    pass


class Reference(collections.UserString):
    """
    example: '/myusername/'
    """

    def __init__(self, _s='', *, _is_empty=True):
        """
        TODO: make compatible with sequence input
        :param _s:
        :param _is_empty:
        """
        if not isinstance(_is_empty, bool):
            import logging
            logging.error(
                f'Expected bool, but received {_is_empty} '
                f'as the value for _is_empty. '
                'Initialize with Reference.from_str where applicable. '
            )
        self._is_empty = _is_empty
        super().__init__(_s)

    def child(self, s):
        if self._is_empty:
            return self.__class__(_s=s, _is_empty=False)
        else:
            return self.__class__(_s=f'{self}/{s}', _is_empty=False)

    @classmethod
    def from_str(cls, s: str):
        if s == '':
            return cls(_is_empty=True, _s=s)
        else:
            return cls(_is_empty=False, _s=s)

    @property
    def first(self):
        return self.data.split('/')[0]  # example: '/myusername/'

    @property
    def last(self):
        return self.data.split('/')[-1]

    @property
    def id(self):
        return self.last

    @property
    def params(self):
        return self.data.split('/')

    @property
    def to_str(self):
        return str(self)

    @property
    def path(self) -> tuple:
        return tuple(self.params)

    @property
    def collection(self):
        raise NotImplementedError

    def __truediv__(self, other):
        """ Overload / operator.
            Example: SomeReference / 'new_path_segment'

        :param other:
        :return:
        """
        return self.child(other)

    def __rtruediv__(self, other):
        raise TypeError('str / Reference is not supported')


reference = Reference()


class Snapshot(collections.UserDict):

    next = property()
    prev = property()

    def __init__(self, *args, __onto_meta__=None, **kwargs):
        """
        TODO: note that in extreme conditions, a document with randomly
        TODO:   generated string key may take on the value of
        TODO:   '__onto_meta__' and thus cause error

        :param args:
        :param __onto_meta__:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if __onto_meta__ is not None:
            for key, val in __onto_meta__.items():
                setattr(self, key, val)

    @next.getter
    def next(self):
        return self._onto_next

    @next.setter
    def next(self, _onto_next):
        self._onto_next = _onto_next

    @prev.getter
    def prev(self):
        return self._onto_prev

    @prev.setter
    def prev(self, _onto_prev):
        self._onto_prev = _onto_prev

    def to_dict(self):
        return self.data.copy()


class Database:

    class Comparators(ConditionArg):
        @property
        def condition(self):
            return self.value

    @classmethod
    @abc.abstractmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get(cls, ref: Reference, transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_many(cls, refs: [Reference], transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def update(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def delete(cls, ref: Reference, transaction=_NA):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def query(cls, q):
        raise NotImplementedError

    ref = reference

    # TODO: NOTE: Should be classmethod
    listener = None


class Listener:

    _registry = dict()
    from ..coordinator import Coordinator
    _coordinator = Coordinator()

    @classmethod
    def for_query(cls):
        pass

    @classmethod
    def for_refs(cls):
        pass


def is_reference(val):
    return issubclass(val.__class__, Reference)


def is_snapshot(val):
    return issubclass(val.__class__, Snapshot)
