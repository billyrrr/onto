import pytest


def test_hello():
    from onto.helpers import make_variable

    ct1 = make_variable('ct1', default='ct1default')
    ct2 = make_variable('ct2', default='ct2default')

    with ct1('ct1a'):
        assert ct1.get() == 'ct1a'
        with ct1('ct1b'):
            assert ct1.get() == 'ct1b'

    assert ct1.get() == 'ct1default'
