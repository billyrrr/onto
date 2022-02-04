from onto.database import Listener, Reference, Snapshot


class GenericListener(Listener):
    from asyncio.queues import Queue
    from collections import defaultdict
    #
    # def create_queue():
    #     from onto.context import Context as CTX

    qs = defaultdict(Queue)

    @classmethod
    def _pub(cls, reference: Reference, snapshot: Snapshot):
        col = reference.collection
        cls.qs[col].put_nowait((reference, snapshot))

    @classmethod
    async def _sub(cls, col):
        while True:
            item = await cls.qs[col].get()
            if item is None:
                break
            try:
                yield item
            except Exception as e:
                from onto.context import Context as CTX
                CTX.logger.exception(f"a task in the queue has failed {item}")
            cls.qs[col].task_done()

    @classmethod
    async def listen(cls, col, source):
        async for ref, snapshot in cls._sub(col):
            await source._invoke_mediator(
                func_name='on_create', ref=ref, snapshot=snapshot)