import pytest

from onto.helpers import unpack_dict


def test_unpack_dict():
    d = dict(foo='bar')
    foo, = unpack_dict(d)
    assert foo == 'bar'

