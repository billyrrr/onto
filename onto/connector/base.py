

class ConnectorBase:
    """
    Connector invokes instance methods of a mediator

    Order:
    1. External component invokes connector._invoke_mediator
    2. _invoke_mediator(*args, **kwargs)
        i.  Locate the instance method of mediator to call: f
        ii. Transform with side effect (*args, **kwargs) -> (*nargs, **nkwargs)
        iii.Call f(*nargs, **nkwargs) -> ret
        iv. Transform with side effect ret -> nret
        v.  return nret

    connector.

    """

    # router: None

    def __init__(self):
        from pymonad.reader import Compose
        self._before_call = Compose(lambda x: x)
        self._after_call = Compose(lambda x: x)

    def before_call(self, f):
        self._before_call = self._before_call.map(f)
        return self

    def after_call(self, f):
        self._after_call = self._after_call.map(f)
        return self

    def invoke_mediator(self, *args, **kwargs):
        from pymonad.reader import Compose
        applicative = Compose(lambda x: x)
        applicative = applicative.map(self._before_call)
        applicative = applicative.map(self._invoke_mediator)
        applicative = applicative.map(self._after_call)
        return applicative(*args, **kwargs)

    def _invoke_mediator(self, *args, **kwargs):
        pass
