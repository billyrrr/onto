
def test_reference():

    from flask_boiler.database import Reference

    r = Reference()
    a = r.child('a')
    ab = a.child('b')
    assert a == 'a'
    assert ab == 'a/b'


def test_reference_truediv():

    from flask_boiler.database import Reference

    r = Reference()
    a = r / 'a'
    ab = a / 'b'
    assert a == 'a'
    assert ab == 'a/b'

    assert a/'c'/'d' == 'a/c/d'
    assert a/'e'/'f'/'g' == 'a/e/f/g'


def test_reference_truediv_eq():
    """ Tests that "/=" creates a new Reference object
    """

    from flask_boiler.database import Reference

    r = Reference()
    r /= 'a'
    pre = id(r)
    assert r == 'a'
    r /= 'b'
    post = id(r)
    assert r == 'a/b'

    assert pre != post


def test_deserialize():

    from flask_boiler.database import Reference

    r = Reference.from_str(s='a/b')

    assert r == 'a/b'
    assert isinstance(r, Reference)
    assert not r._is_empty

    r = Reference.from_str(s='')
    assert r == ''
    assert isinstance(r, Reference)
    assert r._is_empty

    # This behavior is arbitrary and may be changed
    r = Reference.from_str(s='/')
    assert r == '/'
    assert isinstance(r, Reference)
    assert not r._is_empty


def test_serialize():

    from flask_boiler.database import Reference

    r = Reference()
    a = r.child('a')
    ab = a.child('b')
    assert str(a) == 'a'
    assert str(ab) == 'a/b'


def test_leancloud():
    from flask_boiler.database.leancloud import LeancloudDatabase
    from flask_boiler.database import Snapshot

    ref = LeancloudDatabase.ref/'TODO'/'582570f38ac247004f39c24b'
    snapshot = Snapshot(title='foo', priority='bar')
    LeancloudDatabase.set(ref=ref, snapshot=snapshot)
