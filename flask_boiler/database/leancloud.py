import leancloud
from . import Database, Reference, Snapshot
from ..common import _NA


class LeancloudDatabase(Database):

    @classmethod
    def _get_cla(cls, cla_str):
        return leancloud.Object.extend(name=cla_str)

    ref = Reference()

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        object_id = ref.last
        cla = cls._get_cla(ref.first)
        obj = cla(id=object_id, **snapshot.to_dict())
        obj.save()

    @classmethod
    def get(cls, ref: Reference, transaction=_NA):
        object_id = ref.last
        cla = cls._get_cla(ref.first)
        snapshot = Snapshot(cla.query.get(object_id=object_id).dump())
        return snapshot

    @classmethod
    def update(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.set(ref, snapshot, transaction)

    @classmethod
    def create(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.set(ref, snapshot, transaction)

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        object_id = ref.last
        cla = cls._get_cla(ref.first)
        state = cla(id=object_id).destroy()
        if state is None:
            raise ValueError

