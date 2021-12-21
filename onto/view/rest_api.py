from functools import cached_property

from flasgger import SwaggerView
from flask import request, jsonify

from onto.attrs import attrs
from onto.view.base import ViewMediatorBase

from onto.models.base import Serializable


class ParamsParams(Serializable):
    page_size = attrs.int
    current = attrs.int


class Sort(Serializable):
    foo = attrs.string


class Filter(Serializable):
    foo = attrs.string


class Params(Serializable):
    params = attrs.embed(ParamsParams)
    sort = attrs.embed(Sort)
    filter = attrs.embed(Filter)


class ViewMediator(ViewMediatorBase):
    """
    Registers a REST API Resource for a view model
    """

    def __init__(self,
                 view_model_cls=None,
                 mutation_cls=None,
                 *args,
                 app=None,
                 **kwargs):
        """ Initialize a ViewMediator for REST API

        :param view_model_cls
        :param mutation_cls: a subclass of Mutation to handle the changes
                POST, PATCH, UPDATE, PUT, DELETE made to the list of view
                models or a single view model.
        :param args:
        :param app: Flask App
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.view_model_cls = view_model_cls
        self.mutation_cls = mutation_cls
        self.app = app
        self.rule_view_cls_mapping = dict()
        self.default_tag = self.view_model_cls.__name__

    @cached_property
    def paginated_query_cls(_self):
        from onto.models.base import Serializable
        from onto.attrs import attrs
        return type(
            f'{_self.view_model_cls.__name__}PaginatedQueryResponse',
            (Serializable,),
            {
                'total': attrs.integer,
                'data': attrs.list(value=attrs.embed(_self.view_model_cls))
            }
        )

    def add_instance_get(self, rule=None, instance_get_view=None):
        """
        Add GET operation for resource/instance_id

        :param rule: flask url rule
        :param instance_get_view: Flask View
        :return:
        """

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
        """
        Add GET operation for resource to get a list of instances

        :param rule: flask url rule
        :param list_get_view: Flask View
        :return:
        """
        if list_get_view is None:
            list_get_view = self._default_list_get_view()

        name = self.view_model_cls.__name__ + "ListGetView"
        assert rule is not None
        self.app.add_url_rule(
        rule,
        view_func=list_get_view.as_view(name=name),
        methods=['GET']
        )
        self.rule_view_cls_mapping[(rule, 'GET')] = list_get_view

    def add_list_post(self, rule=None, list_post_view=None):
        """
        Add POST operation for resource to add an instance to a list
                of instances

        :param rule: flask url rule
        :param list_post_view: Flask View
        :return:
        """
        if list_post_view is None:
            list_post_view = self._default_list_post_view()
        name = self.view_model_cls.__name__ + "ListPostView"
        assert rule is not None
        self.app.add_url_rule(
            rule,
            view_func=list_post_view.as_view(name=name),
            methods=['POST']
        )
        self.rule_view_cls_mapping[(rule, 'POST')] = list_post_view

    def add_instance_put(self, rule=None, instance_put_view=None):
        """
        Add POST operation for resource to add an instance to a list
                of instances

        :param rule: flask url rule
        :param list_post_view: Flask View
        :return:
        """
        if instance_put_view is None:
            instance_put_view = self._default_instance_put_view()
        name = self.view_model_cls.__name__ + "InstancePutView"
        assert rule is not None
        self.app.add_url_rule(
            rule,
            view_func=instance_put_view.as_view(name=name),
            methods=['PUT']
        )
        self.rule_view_cls_mapping[(rule, 'PUT')] = instance_put_view

    def add_instance_patch(self, rule=None, instance_patch_view=None):
        """
        Add PATCH operation for making changes to an instance

        :param rule: flask url rule
        :param instance_patch_view: Flask View
        :return:
        """

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

    def add_instance_delete(self, rule=None, instance_delete_view=None):
        """ Add DELETE operation for making changes to an instance

        :param rule:
        :param instance_patch_view: Flask View
        :return:
        """

        if instance_delete_view is None:
            instance_delete_view = self._default_instance_delete_view()

        name = self.view_model_cls.__name__ + "InstanceDeleteView"
        assert rule is not None
        self.app.add_url_rule(
            rule,
            view_func=instance_delete_view.as_view(name=name),
            methods=['DELETE']
        )
        self.rule_view_cls_mapping[(rule, 'DELETE')] = instance_delete_view

    def _default_list_post_view(_self):
        """ Returns a default flask view to handle POST to a list of instances

        """

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
                    },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": _self.view_model_cls.get_schema_cls(),
                }
                ]

            def post(self, *args, **kwargs):
                obj = _self.mutation_cls.mutate_create(
                    **kwargs,
                    data=request.json
                )
                if obj is not None:
                    return jsonify(obj.to_dict())
                else:
                    from flask import Response
                    return Response(status=204)
        return PostView

    def _default_instance_patch_view(_self):
        """ Returns a default flask view to handle PATCH to an instance

        """
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
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": _self.view_model_cls.get_schema_cls(),
                }
            ]

            def patch(self, doc_id=None, **kwargs):
                d = {
                    _self.view_model_cls.get_schema_cls().g(key): val
                    for key, val in request.json.items()
                }
                _self.mutation_cls.mutate_patch(
                    doc_id=doc_id, data=d)
                # time.sleep(1)  # TODO: delete after implementing sync
                return jsonify({
                    "operation_status": "success"
                })

        return PatchView

    def _default_instance_put_view(_self):
        """ Returns a default flask view to handle PUT to an instance

        """

        # TODO: change to dynamically construct class to avoid class
        #           name conflict

        class PutView(SwaggerView):
            tags = [_self.default_tag]

            description = "PUT a specific instance "

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
                },
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": _self.view_model_cls.get_schema_cls(),
                }
            ]

            def put(self, doc_id=None, **kwargs):
                obj = _self.mutation_cls.mutate_put(
                    doc_id=doc_id,
                    data=request.json,
                    **kwargs,
                )
                if obj is not None:
                    return jsonify(obj.to_dict())
                else:
                    from flask import Response
                    return Response(status=200)
        return PutView

    def _default_instance_delete_view(_self):
        """ Returns a default flask view to handle PATCH to an instance

        """
        # TODO: change to dynamically construct class to avoid class
        #           name conflict

        class DeleteView(SwaggerView):

            tags = [_self.default_tag]

            description = "Deletes a specific instance "

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

            def delete(self, doc_id=None, **kwargs):
                _self.mutation_cls.mutate_delete(
                    doc_id=doc_id)
                # time.sleep(1)  # TODO: delete after implementing sync
                return jsonify({
                    "operation_status": "success"
                })

        return DeleteView

    def _default_instance_get_view(_self):
        """ Returns a default flask view to handle GET to an instance

        """
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
                instance = _self.view_model_cls.get(*args, **kwargs)
                # time.sleep(1)  # TODO: delete after implementing sync
                return jsonify(instance.to_view_dict())

        return GetView

    def _default_list_get_view(_self):

        class ListGetView(SwaggerView):
            tags = [_self.default_tag]

            description = "Query instance by conditions"

            responses = {
                200: {
                    "description": description,
                    "schema": _self.paginated_query_cls.get_schema_cls()
                }
            }

            parameters = [
                {
                    "name": "params",
                    "in": "path",
                    "type": "object",
                    "required": False,
                },
                {
                    "name": "sort",
                    "in": "path",
                    "type": "object",
                    "required": False,
                },
                {
                    "name": "filter",
                    "in": "path",
                    "type": "object",
                    "required": False,
                },
            ]

            def get(self):
                from flask import request
                params_str = request.args.get('params', '{}')
                sort_str = request.args.get('sort', '{}')
                filter_str = request.args.get('filter', '{}')
                import json

                params_d = json.loads(params_str)
                sort_d = json.loads(sort_str)
                filter_d = json.loads(filter_str)
                params = Params.from_dict({
                    'params': params_d,
                    'sort': sort_d,
                    'filter': filter_d,
                })
                result = list(_self.view_model_cls.get_many())
                paginated = _self.paginated_query_cls.new(
                    data=result,
                    total=0,
                )
                from flask import jsonify
                return jsonify(paginated.to_dict())

        return ListGetView

