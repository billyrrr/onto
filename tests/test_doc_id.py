import pytest

from onto.attrs import attrs
from .fixtures import CTX


def test_deserialize_doc_id(CTX):

    from onto.domain_model import DomainModel

    class MyDomainModel(DomainModel):

        foo = attrs.string

    obj = MyDomainModel.new(
        doc_id='a',
        foo='bar'
    )

    assert obj.doc_id == 'a'

    d = obj.to_dict()
    assert d['doc_id'] == 'a'

    obj_new = MyDomainModel.from_dict(
        d
    )

    assert obj_new.doc_id == 'a'

