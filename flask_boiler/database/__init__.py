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

    ref = reference

    listener = None


class Listener:

    def on_write(self):
        pass
