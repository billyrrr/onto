import collections
import abc

from flask_boiler.common import _NA


class Reference(collections.UserString):
    """
    example: '/myusername/'
    """

    def __init__(self, _is_empty=True, _s=''):
        self._is_empty = _is_empty
        super().__init__(_s)

    def child(self, s):
        if self._is_empty:
            return self.__class__(_is_empty=False, _s=s)
        else:
            return self.__class__(_is_empty=False, _s=f'{self}/{s}')

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

    def __init__(self, *args, __flask_boiler_meta__=None, **kwargs):
        """
        TODO: note that in extreme conditions, a document with randomly
        TODO:   generated string key may take on the value of
        TODO:   '__flask_boiler_meta__' and thus cause error

        :param args:
        :param __flask_boiler_meta__:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if __flask_boiler_meta__ is not None:
            for key, val in __flask_boiler_meta__.items():
                setattr(self, key, val)

    @next.getter
    def next(self):
        return self._flask_boiler_next

    @next.setter
    def next(self, _flask_boiler_next):
        self._flask_boiler_next = _flask_boiler_next

    @prev.getter
    def prev(self):
        return self._flask_boiler_prev

    @prev.setter
    def prev(self, _flask_boiler_prev):
        self._flask_boiler_prev = _flask_boiler_prev

    def to_dict(self):
        return self.data.copy()


class Database:

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
