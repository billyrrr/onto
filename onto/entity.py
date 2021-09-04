 from onto.primary_object import PrimaryObject


class Entity(PrimaryObject):
    """
    Entity is for flink stateful functions
    """

    @classmethod
    def _datastore(cls):
        from onto.context import Context as CTX
        return CTX.db


import statefun

functions = statefun.StatefulFunctions()

handler = statefun.RequestReplyHandler(functions)


from dataclasses import dataclass


def register_root_entity(entity):

    functions.register()


def method_invoked(context, call_event: CallEvent):
    state = context.state('_internal_state').unpack(InternalState)
    if not state:
        state = SeenCount()
        state.seen = 1
    else:
        state.seen += 1
    context.state('seen_count').pack(state)

    response = compute_greeting(greet_request.name, state.seen)

    egress_message = kafka_egress_record(topic="greetings", key=greet_request.name, value=response)
    context.pack_and_send_egress("example/greets", egress_message)


class MethodSerializer:
    """
    (Internal)

    Ref: https://stackoverflow.com/questions/5103735/better-way-to-log-method-calls-in-python
    """

    def _decorator(self, f):
        import functools
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            handler()
            context.send(typename=self.doc_ref.collection, id=self.doc_ref.id, message=Any)
            return (f.__name__, args, kwargs)
        return wrapper

    def __getattribute__(self, item):

        # def f(*args, **kwargs):
        #     raise ValueError('Should not have been called')

        value = object.__getattribute__(self, item)
        if callable(value):
            decorator = object.__getattribute__(self, '_decorator')
            return decorator(value)
        return value


class EntityProxy(PrimaryObject):
    """


    Useful: https://docs.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/communication-in-microservice-architecture
    """

    pass

        #
        # statefun.kafka_egress_record()
        # func_addr

