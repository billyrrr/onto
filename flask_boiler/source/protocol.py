class Protocol:

    def __init__(self):
        self.mapping = dict()

    def _register(self, rule):
        def decorator(f):
            self.mapping[rule] = f.__name__
            return f
        return decorator

    def fname_of(self, rule):
        if rule in self.mapping:
            return self.mapping[rule]
        else:
            return None

    def __getattr__(self, item):
        return self._register(item)
