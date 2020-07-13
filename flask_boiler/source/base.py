import weakref

from flask_boiler.source.protocol import Protocol


class Source:

    def __set_name__(self, owner, name):
        """ Keeps mediator as a weakref to protect garbage collection
        Note: mediator may be destructed if not maintained or referenced
            by another variable. Mediator needs to be explicitly kept alive.

        :param owner:
        :param name:
        :return:
        """
        self.parent = weakref.ref(owner)

    def __init__(self):
        """ Initializes a ViewMediator to declare protocols that
                are called when the results of a query change. Note that
                mediator.start must be called later.

        :param query: a listener will be attached to this query
        """
        self.protocol = Protocol()

    @property
    def triggers(self):
        return self.protocol