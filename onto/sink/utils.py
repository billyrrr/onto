import asyncio
from collections import defaultdict
from typing import AsyncGenerator


class Broker:
    """
    Broker

    WARNING: unsubscribe is not implemented. RAM size will instead increase when the
    subscriber exited, since the stored topics are not consumed.

    RECOMMENDATION: (work-around) limit RAM size so that the container would reboot when out of memory.

    """

    def __init__(self):
        self.source_queue = asyncio.Queue()
        self.source_sink_mapping = defaultdict(list)
        self.sink_queue = defaultdict(asyncio.Queue)

    def bind(self, *, pub_id, sub_id):
        self.source_sink_mapping[pub_id].append(sub_id)

    async def publish(self, topic_name, item):
        await self.source_queue.put((topic_name, item))

    async def source_while_loop(self):
        while True:
            pub_id, item = await self.source_queue.get()
            for sub_id in self.source_sink_mapping[pub_id]:
                q: asyncio.Queue = self.sink_queue[sub_id]
                await q.put(item)

    async def sink_while_loop(self, sub_id) -> AsyncGenerator:
        while True:
            self.sink_queue[sub_id]: asyncio.Queue
            item = self.sink_queue[sub_id].get()
            yield item
            self.sink_queue[sub_id].task_done()
