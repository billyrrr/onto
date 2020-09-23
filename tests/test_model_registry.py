import onto.models.base


class RModelSup(onto.models.base.BaseRegisteredModel):
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


def test_get_subclasses():
    assert RModelSup._get_subclasses() == {RModelSup, RModelA, RModelAB, RModelB}


def test_get_subclasses_str():
    assert RModelSup._get_subclasses_str() == \
           ["RModelA", "RModelAB", "RModelB", "RModelSup"]


def test_register_subclass():

    class CModelParent(onto.models.base.BaseRegisteredModel):
        pass

    class CModelChild(CModelParent):
        pass

    assert CModelChild.__name__ == "CModelChild"
