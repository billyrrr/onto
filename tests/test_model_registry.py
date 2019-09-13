from flask_boiler import model_registry


class RModelSup(model_registry.BaseRegisteredModel):
    pass


class RModelA(RModelSup):
    pass


class RModelAB(RModelA):
    pass


class RModelB(RModelSup):
    pass


def test_get_cls_from_name():
    assert RModelSup.get_cls_from_name("RModelSup") == RModelSup


def test_tree():
    assert RModelSup._tree["RModelSup"] == {"RModelA", "RModelB"}


def test_get_children():

    assert RModelSup._get_children() == {RModelA, RModelB}
    assert RModelA._get_parents() == {RModelSup,}

