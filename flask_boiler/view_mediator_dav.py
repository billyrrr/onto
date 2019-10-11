import time

from flasgger import SwaggerView
from flask import request

from flask_boiler.domain_model import DomainModel


class ViewMediatorDAV:
    """
    Watches and updates Firestore for DocumentAsView view models
    """

    def __init__(self,
                 view_model_cls=None,
                 mutation_cls=None):
        """

        :param view_model_cls: the view model to be exposed in REST API
        :param app: Flask App
        :param mutation_cls: a subclass of Mutation to handle the changes
                POST, PATCH, UPDATE, PUT, DELETE made to the list of view
                models or a single view model.
        """
        self.view_model_cls = view_model_cls
        self.mutation_cls = mutation_cls
        self.rule_view_cls_mapping = dict()
        self.default_tag = self.view_model_cls.__name__
        self.instances = dict()


