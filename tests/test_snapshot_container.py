from onto.store import SnapshotContainer


def test_set_with_timestamp():
    container = SnapshotContainer()
    container.set_with_timestamp('k', 'v', (1, 0))
    assert container.get('k', (1, 0)) == 'v'


def test_has_previous():
    container = SnapshotContainer()
    assert not container.has_previous('k')
    container.set_with_timestamp('k', 'v', (1, 0))
    assert container.has_previous('k')


def test_previous():
    container = SnapshotContainer()
    container.set_with_timestamp('k', 'v1', (1, 0))
    assert container.previous('k') == 'v1'
    container.set_with_timestamp('k', 'v2', (2, 0))
    assert container.previous('k') == 'v2'


def test_get_with_range():
    container = SnapshotContainer()
    container.set_with_timestamp('k', 'v1', (1, 0))
    container.set_with_timestamp('k', 'v2', (2, 0))
    assert list(container.get_with_range(
        key='k',
        lo_excl=(1, 0),
        hi_incl=(2, 0)
    )) == ['v2']
    assert list(container.get_with_range(
        key='k',
        hi_incl=(2, 0)
    )) == ['v1', 'v2']
