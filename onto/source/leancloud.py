from onto.source.base import Source
from onto.context import Context as CTX


class LeancloudHook(Source):

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def start(self):
        self._register()

    def _register(self):
        engine = CTX.services.engine
        for trigger_name in self.protocol.mapping:
            wrapper_f = getattr(engine, trigger_name)
            wrapper = wrapper_f(self.class_name)

            @wrapper
            def f(*args, **kwargs):
                from functools import partial
                f = partial(self._call, trigger_name=trigger_name)
                return f(*args, **kwargs)

    def _call(self, cla_obj, *, trigger_name):
        from onto.database.leancloud import LeancloudSnapshot, LeancloudReference
        snapshot = LeancloudSnapshot.from_cla_obj(cla_obj)
        ref = LeancloudReference.from_cla_obj(cla_obj)
        self._invoke_mediator(
            func_name=trigger_name,
            ref=ref,
            snapshot=snapshot
        )


class DomainModelSource(LeancloudHook):

    def __init__(self, domain_model_cls):
        super().__init__(class_name=domain_model_cls._get_collection_name())
        self.domain_model_cls = domain_model_cls

    def _call(self, trigger_name, cla_obj):
        from onto.database.leancloud import LeancloudSnapshot

        from onto.database.leancloud import LeancloudReference
        ref = LeancloudReference.from_cla_obj(cla_obj)
        snapshot = LeancloudSnapshot.from_cla_obj(cla_obj)
        obj = self.domain_model_cls.from_snapshot(ref=ref, snapshot=snapshot)
        self._invoke_mediator(
            func_name=trigger_name,
            obj=obj
        )

# before_save = LeancloudBeforeSaveSource
hook = LeancloudHook
domain_model_hook = DomainModelSource
