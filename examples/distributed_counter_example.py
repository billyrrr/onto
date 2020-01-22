from flask_boiler import fields
from flask_boiler.business_property_store import BPSchema
from flask_boiler.context import Context as CTX
from flask_boiler.schema import Schema
from flask_boiler.fields import Integer
from flask_boiler.domain_model import DomainModel
from flask_boiler.struct import Struct
from flask_boiler.view_mediator_dav import ViewMediatorDAV
from flask_boiler.view_model import ViewModel


class ShardSchema(Schema):

    count = Integer()


class Shard(DomainModel):

    class Meta:
        schema_cls = ShardSchema


class CounterViewSchema(Schema):

    total_count = Integer(dump_only=True)


class ShardsStoreBpss(BPSchema):
    shards = fields.StructuralRef(dm_cls=Shard, many=True)


class CounterView(ViewModel):

    class Meta:
        schema_cls = CounterViewSchema

    def __init__(self, *args, **kwargs):
        doc_ref = CTX.db.collection("counters").document("counter_0")
        super().__init__(*args, doc_ref=doc_ref, **kwargs)
        self.shards = dict()

    @property
    def total_count(self):
        return sum(v.count for _, v in self.store.shards.items())

    def set_shard(self, sid, shard):
        self.shards[sid] = shard

    def get_vm_update_callback(self, dm_cls, *args, **kwargs) :

        if dm_cls == Shard:
            def callback(vm: CounterView, dm: Shard):
                vm.set_shard(dm.doc_id, dm)
            return callback
        else:
            return super().get_vm_update_callback(dm_cls, *args, **kwargs)


class CounterMediator(ViewMediatorDAV):

    def __init__(self, shard_size, *args, **kwargs):
        super().__init__(*args, view_model_cls=CounterView, **kwargs)
        self.shard_size = shard_size
        self.view_model = None

    @classmethod
    def notify(cls, obj):
        obj.save()

    def start(self):

        struct = Struct(schema_obj=ShardsStoreBpss())

        for i in range(self.shard_size):
            doc_id = str(i)
            shard = Shard.new(doc_id=doc_id, )
            shard.save()
            struct["shards"][shard.doc_id] = (Shard, doc_id)

        self.view_model = self.view_model_cls.get(
            f_notify=self.notify,
            struct_d=struct,
            once=False)
