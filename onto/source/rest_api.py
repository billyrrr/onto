from onto.source.rest import Source, RestProtocol


class StarletteConnector(Source):
    """
    @some_connector.triggers.route('/callback', ('POST',))
    async def some_method(self, request):
    """

    _protocol_cls = RestProtocol

    def route(self, *args, **kwargs):
        return self.protocol.route(*args, **kwargs)
        # protocol: RestProtocol = self.protocol

    def __init__(self, *args, **kwargs):
        self._mediator_instance = None
        super().__init__(*args, **kwargs)

    # def emit(self, res):
    #     abort(res)

    @property
    def mediator_instance(self):
        if self._mediator_instance is None:
            self._mediator_instance = self.parent()()
        return self._mediator_instance

    def start(self, url_prefix=None):
        from starlette.routing import Route

        routes = list()
        # bp = Blueprint(self.parent().__name__, __name__, url_prefix=url_prefix)
        for rule, methods, f_name in self.protocol._get_functions():
            async def routable(*args, **kwargs):
                return await self._invoke_mediator_async(func_name=f_name, *args,  **kwargs)

            route = Route(path=rule, endpoint=routable, methods=methods)
            routes.append(route)

        from starlette.routing import Mount
        mount = Mount(url_prefix, routes=routes)

        return [mount]