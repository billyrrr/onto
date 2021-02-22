import contextlib
import contextvars


class ContextVariable(contextlib.ContextDecorator):
    stack = list()
    var: contextvars.ContextVar = None

    def __init__(self, next_var):
        self.next_var = next_var

    def __enter__(self):
        # TODO: not atomic when multithreading
        self.stack.append(self.var.set(self.next_var))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.var.reset(self.stack.pop())
        return False

    @classmethod
    def get(cls):
        return cls.var.get()


def make_variable(name, **kwargs):
    class InlineContextVariable(ContextVariable):
        var = contextvars.ContextVar(name, **kwargs)
    return InlineContextVariable
