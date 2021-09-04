from onto.attrs.unit import Monad, MonadContext


def test_monad():
    r = Monad._get_root()
    str_optional = r.str.optional
    assert str_optional.properties.type_cls == str
    assert not str_optional.properties.import_required
    assert not str_optional.properties.export_required

    s_int_optional = r.str.int.optional
    assert s_int_optional.properties.type_cls == int
    assert not s_int_optional.properties.import_required
    assert not s_int_optional.properties.export_required


def test_monad_inherit():
    r = Monad._get_root()
    int_a = r.optional
    assert not hasattr(int_a.properties, 'type_cls')
    assert not int_a.properties.import_required

    with MonadContext.context().int:
        assert int_a.properties.type_cls == int


def test_monad_list():

    r = Monad._get_root()
    li = r.list(
        value=lambda a: a.str.optional
    ).required
    assert li.properties.import_required
    assert li.properties.export_required

    assert li.properties.list_value.properties.type_cls == str
    assert not li.properties.list_value.properties.import_required
    assert not li.properties.list_value.properties.export_required


def test_list_decorate():

    r = Monad._get_root()
    li2 = r.list(
        value=lambda a: a.optional
    ).required

    assert not li2.properties.list_value.properties.import_required
    assert not li2.properties.list_value.properties.export_required

    assert not hasattr(li2.properties.list_value.properties, 'type_cls')
    with MonadContext.context().data_key('my_list'):
        assert li2.properties.data_key == 'my_list'
        assert not hasattr(li2.properties.list_value.properties, 'type_cls')


def test_list_inherit_complex():
    r = Monad._get_root()
    li2 = r.list(
        value=lambda a: a.optional
    ).required

    assert not li2.properties.list_value.properties.import_required
    assert not li2.properties.list_value.properties.export_required

    assert not hasattr(li2.properties.list_value.properties, 'type_cls')
    with MonadContext.context().list(
        value=lambda a: a.str
    ):
        assert li2.properties.list_value.properties.type_cls == str
