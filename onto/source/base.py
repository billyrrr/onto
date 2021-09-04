import weakref

from onto.source.protocol import Protocol


class SourceBase:

    def __set_name__(self, owner, name):
        """ Keeps mediator as a weakref to protect garbage collection
        Note: mediator may be destructed if not maintained or referenced
            by another variable. Mediator needs to be explicitly kept alive.

        :param owner:
        :param name:
        :return:
        """
        self.parent = weakref.ref(owner)


class Source(SourceBase):

    _protocol_cls = Protocol

    def __init__(self):
        """ Initializes a ViewMediator to declare protocols that
                are called when the results of a query change. Note that
                mediator.start must be called later.

        :param query: a listener will be attached to this query
        """
        self.protocol = self._protocol_cls()

    @property
    def triggers(self):
        return self.protocol

    @property
    def mediator_instance(self):
        return self.parent()()

    def _invoke_mediator(self, *args, func_name, **kwargs):
        fname = self.protocol.fname_of(func_name)
        # TODO: fix: listener close invokes unintended on_delete
        if fname is None:
            raise ValueError(
                f"fail to locate {func_name}"
                f" for {self.mediator_instance.__class__.__name__}"
            )
        f = getattr(self.mediator_instance, fname)
        f(*args, **kwargs)

    async def _invoke_mediator_async(self, *args, func_name, **kwargs):
        fname = self.protocol.fname_of(func_name)
        # TODO: fix: listener close invokes unintended on_delete
        if fname is None:
            raise ValueError(
                f"fail to locate {func_name}"
                f" for {self.mediator_instance.__class__.__name__}"
            )
        f = getattr(self.mediator_instance, fname)
        return await f(*args, **kwargs)
