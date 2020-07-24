from flask_boiler.source.base import Source
from flask_boiler.context import Context as CTX


class LeancloudBeforeSaveSource(Source):

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def start(self):
        self._register()

    def _register(self):
        engine = CTX.services.engine
        engine.before_save(self.class_name, self._call)

    def _call(self, cla_obj):
        from flask_boiler.database.leancloud import LeancloudSnapshot, LeancloudReference
        snapshot = LeancloudSnapshot.from_cla_obj(cla_obj)
        ref = LeancloudReference.from_cla_obj(cla_obj)
        self._invoke_mediator(
            func_name='before_save',
            ref=ref,
            snapshot=snapshot
        )


class BeforeSaveDomainModelSource(LeancloudBeforeSaveSource):

    def __init__(self, domain_model_cls):
        super().__init__(class_name=domain_model_cls._get_collection_name())
        self.domain_model_cls = domain_model_cls

    def _call(self, cla_obj):
        from flask_boiler.database.leancloud import LeancloudSnapshot

        from flask_boiler.database.leancloud import LeancloudReference
        ref = LeancloudReference.from_cla_obj(cla_obj)
        snapshot = LeancloudSnapshot.from_cla_obj(cla_obj)
        obj = self.domain_model_cls.from_snapshot(ref=ref, snapshot=snapshot)
        self._invoke_mediator(
            func_name='before_save',
            obj=obj
        )

before_save = LeancloudBeforeSaveSource
