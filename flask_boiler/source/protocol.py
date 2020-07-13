class Protocol:

    def __init__(self):
        self.mapping = dict()

    def _register(self, rule):
        def decorator(f):
            self.mapping[rule] = f.__name__
            return f
        return decorator

    def fname_of(self, rule):
        return self.mapping[rule]

    def __getattr__(self, item):
        return self._register(item)