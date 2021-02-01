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
        await super()._invoke_mediator_async(func_name=func_name, obj=obj)

    def start(self, loop):
        self._register(loop=loop)

    import asyncio

    def _register(self, loop: asyncio.BaseEventLoop):
        from onto.context import Context as CTX
        _awaitable = self.dm_cls._datastore().listener().listen(col=self.dm_cls._get_collection_name(), source=self)
        _ = loop.create_task(_awaitable)

