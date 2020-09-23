
class Sink:

    def emit(self):
        pass

    def close(self):
        pass

    def emit_and_close(self, *args, **kwargs):
        pass

    def insert(self):
        pass

    def update(self):
        pass

    def upsert(self):
        pass

    def remove(self):
        pass
