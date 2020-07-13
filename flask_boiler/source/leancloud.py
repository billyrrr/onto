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

    def _call(self, *args, **kwargs):
        raise NotImplementedError


