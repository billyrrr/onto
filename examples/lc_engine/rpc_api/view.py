from onto.context import Context as CTX

CTX.load()

engine = CTX.services.engine


from onto.view import Mediator


# class TodoMediatorLc(Mediator):
#
#     from onto.source.leancloud import hook
#     from onto.sink.json_rpc import sink
#
#     src = hook('Todo')
#     snk = sink(uri=f'{JSONRPC_URI}/todo')
#
#     @src.triggers.after_save
#     def call_after_save_rpc(self, ref, snapshot):
#         self.snk.emit('after_save', ref=str(ref), snapshot=snapshot)
#     #
#     # @src.triggers.before_save
#     # def fb_before_todo_save(self, ref, snapshot):
#     #     from onto.database.firestore import FirestoreReference
#     #     CTX.dbs.firestore.set(ref=FirestoreReference.from_str(str(ref)), snapshot=snapshot)
#     #     raise ValueError(f"{str(ref)} {str(snapshot)}")
#
#     @classmethod
#     def start(cls):
#         cls.src.start()


class TodoMediator(Mediator):

    from onto.source.json_rpc import JsonRpcSource as source
    src = source(url_prefix='/todo')

    @src.triggers.after_save
    def record_todo(self, ref, snapshot):

        from onto.database.firestore import FirestoreReference
        from onto.database import Snapshot
        CTX.dbs.firestore.set(ref=FirestoreReference.from_str(ref),
                              snapshot=Snapshot(snapshot))
        raise ValueError(f"{str(ref)} {str(snapshot)}")

    @classmethod
    def start(cls, app):
        cls.src.start(app)
