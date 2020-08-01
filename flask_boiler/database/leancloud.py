import leancloud
from . import Database, Reference, Snapshot
from ..common import _NA
from ..query.query import Query

LEANCLOUD_DOC_ID_DATA_KEY = '_doc_id'

class LeancloudDatabase(Database):

    class Comparators(Database.Comparators):

        eq = 'equal_to'
        gt = 'greater_than'
        ge = 'greater_than_or_equal_to'
        lt = 'less_than'
        le = 'less_than_or_equal_to'

        _in = 'contained_in'

    @classmethod
    def _get_cla(cls, cla_str):
        return leancloud.Object.extend(name=cla_str)

    ref = Reference()

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        object_id = ref.last
        cla = cls._get_cla(ref.first)
        obj = cla(_doc_id=object_id, **snapshot.to_dict())
        obj.save()

    @classmethod
    def get(cls, ref: Reference, transaction=_NA):
        _doc_id = ref.last
        cla = cls._get_cla(ref.first)
        cla_obj = cla.query.equal_to(LEANCLOUD_DOC_ID_DATA_KEY, _doc_id).first()
        d = LeancloudSnapshot.from_cla_obj(cla_obj).to_dict()
        d['doc_id'] = d.pop(LEANCLOUD_DOC_ID_DATA_KEY)
        snapshot = LeancloudSnapshot(d)
        return snapshot

    @classmethod
    def update(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.set(ref, snapshot, transaction)

    @classmethod
    def create(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.set(ref, snapshot, transaction)

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        """ Note: this only deletes one instance that has _doc_id == ref.last

        :param ref:
        :param transaction:
        :return:
        """
        _doc_id = ref.last
        cla = cls._get_cla(ref.first)
        cla_obj = cla.query.equal_to(LEANCLOUD_DOC_ID_DATA_KEY, _doc_id).first()
        cla_obj.destroy()

    @classmethod
    def query(cls, q: Query):
        for cla_obj in q._to_leancloud_query().find():
            ref = LeancloudReference.from_cla_obj(cla_obj)
            snapshot = LeancloudSnapshot.from_cla_obj(cla_obj)
            yield (ref, snapshot)


class LeancloudSnapshot(Snapshot):
    """
    TODO: apply to LeancloudDatabase class and other places
    """

    @classmethod
    def from_cla_obj(self, cla_obj):
        snapshot = Snapshot(cla_obj.dump())
        return snapshot


class LeancloudReference(Reference):

    @classmethod
    def from_cla_obj(cls, cla_obj):
        ref = cls()/cla_obj._class_name/cla_obj.get('_doc_id', cla_obj.id)
        return ref
