import functools
from queue import Queue
from threading import Thread


class Coordinator:
    """ Manages a task queue.
    Listener adds function invocations to the task queue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = Queue()
        self._start_thread()

    # def start(self):
    #     self._start_thread()

    def _main(self):
        """ Push None to self.q to stop the thread

        :return:
        """
        while True:
            item = self.q.get()
            if item is None:
                break
            try:
                item()
            except Exception as e:
                from onto.context import Context as CTX
                CTX.logger.exception(f"a task in the queue has failed {item}")
            self.q.task_done()

    def _start_thread(self):
        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def _add_awaitable(self, item):
        """ TODO: test

        :param item:
        :return:
        """
        self.q.put(item)
