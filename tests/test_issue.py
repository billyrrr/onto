import pytest

from onto.attrs import attrs


def test_s():

    from onto.view_model import ViewModel

    from onto.view_model import ViewModelR

    class A(ViewModel):
        # foo = attrs.string
        doc_id = attrs.doc_id

    a = A.new(doc_id='foo')
    assert a.doc_id == 'foo'
