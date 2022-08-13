import contextlib
import contextvars

from inflection import camelize

from asyncio.locks import Lock

class ContextVariable(contextlib.ContextDecorator):
    var: contextvars.ContextVar = None  # ABSTRACT

    def __init__(self, next_var):
        self.next_var = next_var
        self.prev_var = None

    def __enter__(self):
        # TODO: not atomic when multithreading
        prev_var = self.var.set(self.next_var)
        self.prev_var = prev_var

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.var.reset(self.prev_var)
        return False

    @classmethod
    def get(cls):
        return cls.var.get()


def make_variable(name, **kwargs):
    class InlineContextVariable(ContextVariable):
        var = contextvars.ContextVar(name, **kwargs)
    return InlineContextVariable


def unpack_dict(d):
    import inspect
    from onto.helpers.unpack_tuple_ported import get_assigned_name
    names = get_assigned_name(inspect.currentframe().f_back)
    for name in names:
        yield d[name]
    yield from ()


def unpack_dict_decamelize(d):
    import inspect
    from onto.helpers.unpack_tuple_ported import get_assigned_name
    names = get_assigned_name(inspect.currentframe().f_back)
    for name in names:
        yield d[camelize(name, uppercase_first_letter=False)]
    yield from ()
