from flasgger import SwaggerView


class ViewMediator:

    def __init__(self, view_model_cls=None, app=None):
        self.view_model_cls = view_model_cls
        self.app = app

    def add_instance_get(self, rule=None, instance_get_view=None):

        if instance_get_view is None:
            instance_get_view = self._default_instance_get_view()

        name = self.view_model_cls.__name__ + "GetView"
        assert rule is not None
        self.app.add_url_rule(
        rule,
        view_func=instance_get_view.as_view(name=name),
        methods=['GET']
        )

    def add_list_get(self, rule=None, list_get_view=None):

        name = self.view_model_cls.__name__ + "GetView"
        assert rule is not None
        self.app.add_url_rule(
        rule,
        view_func=list_get_view.as_view(name=name),
        methods=['GET']
        )

    def _default_instance_get_view(_self):
        # TODO: change to dynamically construct class to avoid class
        #           name conflict

        class GetView(SwaggerView):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.description = "A REST API resource automatically generated by" \
                                   " flask-boiler"

                self.responses = {
                    200: {
                        "description": self.description,
                        "schema": _self.view_model_cls.get_schema_cls()
                    }
                }

                self.parameters = [
                    {
                        "name": "doc_id",
                        "in": "path",
                        "type": "string",
                        "enum": ["all", "palette_id_a",
                                 "palette_id_b"],
                        "required": True,
                        "default": "all"
                    }
                ]

            def get(self, *args, **kwargs):
                return _self.view_model_cls.new(*args,
                                                     **kwargs).to_view_dict()

        return GetView



