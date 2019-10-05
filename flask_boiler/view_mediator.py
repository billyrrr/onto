import time

from flasgger import SwaggerView
from flask import request


class ViewMediator:

    def __init__(self, view_model_cls=None, app=None, mutation_cls=None):
        self.view_model_cls = view_model_cls
        self.app = app
        self.mutation_cls = mutation_cls
        self.rule_view_cls_mapping = dict()
        self.default_tag = self.view_model_cls.__name__

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

        self.rule_view_cls_mapping[(rule, 'GET')] = instance_get_view

    def add_list_get(self, rule=None, list_get_view=None):

        name = self.view_model_cls.__name__ + "ListGetView"
        assert rule is not None
        self.app.add_url_rule(
        rule,
        view_func=list_get_view.as_view(name=name),
        methods=['GET']
        )
        self.rule_view_cls_mapping[(rule, 'GET')] = list_get_view

    def add_list_post(self, rule=None, list_post_view=None):
        name = self.view_model_cls.__name__ + "ListPostView"
        assert rule is not None
        self.app.add_url_rule(
            rule,
            view_func=list_post_view.as_view(name=name),
            methods=['POST']
        )
        self.rule_view_cls_mapping[(rule, 'POST')] = list_post_view

    def add_instance_patch(self, rule=None, instance_patch_view=None):

        if instance_patch_view is None:
            instance_patch_view = self._default_instance_patch_view()

        name = self.view_model_cls.__name__ + "InstancePatchView"
        assert rule is not None
        self.app.add_url_rule(
            rule,
            view_func=instance_patch_view.as_view(name=name),
            methods=['PATCH']
        )
        self.rule_view_cls_mapping[(rule, 'PATCH')] = instance_patch_view

    def _default_list_post_view(_self):

        class PostView(SwaggerView):

            tags = [_self.default_tag]

            description = "Adds an instance to a list "

            responses = {
                    200: {
                        "description": description,
                        "schema": _self.view_model_cls.get_schema_cls()
                    }
                }

            parameters = [
                    {
                        "name": "doc_id",
                        "in": "path",
                        "type": "string",
                        "required": True,
                    }
                ]

            def post(self, *args, doc_id=None, **kwargs):
                _self.mutation_cls.mutate_create(
                    doc_id=doc_id,
                    data=request.json
                )

        return PostView

    def _default_instance_patch_view(_self):
        # TODO: change to dynamically construct class to avoid class
        #           name conflict

        class PatchView(SwaggerView):

            tags = [_self.default_tag]

            description = "Patches a specific instance "

            responses = {
                200: {
                    "description": description,
                    "schema": _self.view_model_cls.get_schema_cls()
                }
            }

            parameters = [
                {
                    "name": "doc_id",
                    "in": "path",
                    "type": "string",
                    "required": True,
                }
            ]

            def patch(self, doc_id=None, **kwargs):
                d = {
                    _self.view_model_cls.get_schema_cls().g(key): val
                    for key, val in request.json.items()
                }
                _self.mutation_cls.mutate_patch(
                    doc_id=doc_id, data=d)
                time.sleep(1)  # TODO: delete after implementing sync
                return {
                    "operation_status": "success"
                }

        return PatchView

    def _default_instance_get_view(_self):
        # TODO: change to dynamically construct class to avoid class
        #           name conflict

        class GetView(SwaggerView):

            tags = [_self.default_tag]

            description = "Gets an instance "

            responses = {
                200: {
                    "description": description,
                    "schema": _self.view_model_cls.get_schema_cls()
                }
            }

            parameters = [
                {
                    "name": "doc_id",
                    "in": "path",
                    "type": "string",
                    "required": True,
                }
            ]

            def get(self, *args, **kwargs):
                instance = _self.view_model_cls.new(*args, **kwargs)
                time.sleep(1)  # TODO: delete after implementing sync
                return instance.to_view_dict()

        return GetView



