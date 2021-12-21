from onto.common import _NA
from onto.database import Database, Reference, Snapshot, Listener
from onto.query.query import Query


class MockReference(Reference):

    def is_collection(self):
        return len(self.params) % 2 == 1

    @property
    def collection(self):
        return self.first

    def is_document(self):
        return len(self.params) % 2 == 0


class MockDatabase(Database):

    class Comparators(Database.Comparators):

        eq = lambda a, b: a == b
        gt = lambda a, b: a > b
        ge = lambda a, b: a >= b
        lt = lambda a, b: a < b
        le = lambda a, b: a <= b
        contains = lambda a, b: a.has(b)  # TODO; check
        _in = lambda a, b: a in b

    @classmethod
    def listener(cls):
        return MockListener

    d = dict()

    ref = MockReference()

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.d[str(ref)] = snapshot.to_dict()
        cls.listener()._pub(reference=ref, snapshot=snapshot)

    @classmethod
    def get(cls, ref: Reference, transaction=_NA):
        return Snapshot(cls.d[str(ref)])

    update = set
    create = set

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        """ Note: this only deletes one instance that has _doc_id == ref.last

        :param ref:
        :param transaction:
        :return:
        """
        del cls.d[str(ref)]

    @classmethod
    def query(cls, q):
        qualifier = q._to_qualifier()
        for k, v in cls.d.items():
            if qualifier(v):
                yield MockReference.from_str(k), Snapshot(v)
        yield from ()


class MockListener(Listener):
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

