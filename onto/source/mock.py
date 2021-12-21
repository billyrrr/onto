from typing import Type

from onto.domain_model import DomainModel
from onto.source.base import Source


class MockDomainModelSource(Source):

    def __init__(self, dm_cls: Type[DomainModel]):
        super().__init__()
        self.dm_cls: Type[DomainModel] = dm_cls
        self.thread = None

    async def _invoke_mediator(self, *, func_name, ref, snapshot):
        obj = self.dm_cls.from_snapshot(ref=ref, snapshot=snapshot)
        try:
            await super()._invoke_mediator_async(func_name=func_name, obj=obj)
        except Exception as _:
            import logging
            logging.exception(f'async _invoke_mediator failed for {func_name} {str(ref)}')

    def start(self, loop=None):
        if loop is None:
            import asyncio
            loop = asyncio.get_event_loop()
        self._register(loop=loop)

    import asyncio

    def _get_awaitable(self):
        return self.dm_cls._datastore().listener().listen(col=self.dm_cls._get_collection_name(), source=self)

    def _register(self, loop: asyncio.BaseEventLoop):
        from onto.context import Context as CTX
        _awaitable = self._get_awaitable()
        _ = loop.create_task(_awaitable)


    def get_all(self):
        return self.dm_cls._datastore().listener().get_all(col=self.dm_cls._get_collection_name())
