from flasgger import SwaggerView
from flask import jsonify

from flask_boiler.firestore_object import SerializableFO
from flask_boiler.referenced_object import ReferencedObject
from .serializable import Serializable
from .domain_model import DomainModel
from .view_model import ViewModel, ViewModelMixin, PersistableMixin
from google.cloud import firestore
from .context import Context as CTX


class FlaskAsViewMixin:

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Abstract method. Subclass implement this method so that a view
                model can be constructed by a single key. Implementing
                or linking this method allows ViewMediator to add
                automatically generated REST API views.

        Should override in subclass
        :param args:
        :param kwargs:
        :return:
        """
        return super().new(*args, **kwargs)

    # def _bind_to_once(self, key, obj_type, doc_id):
    #     """ Gets value of view models without using on_snapshot/listeners
    #
    #     :param key:
    #     :param obj_type:
    #     :param doc_id:
    #     :return:
    #     """
    #     obj_cls: DomainModel = Serializable.get_cls_from_name(obj_type)
    #     dm_ref = obj_cls._get_collection().document(doc_id)
    #     update_func = self._structure[key][2]
    #     on_update = self.get_on_update(dm_cls=obj_cls, dm_doc_id=doc_id,
    #               update_func=update_func, key=None)
    #     # doc_watch = dm_ref.on_snapshot(on_update)
    #     # doc_watch.unsubscribe()
    #     on_update([dm_ref.get()], changes=None, readtime=None)


class FlaskAsView(FlaskAsViewMixin,
                  ViewModelMixin,
                  PersistableMixin,
                  SerializableFO
                  ):
    """
    Base for a view model intended to be exposed as a REST API resource
    """

    @classmethod
    def new(cls, **kwargs):
        obj = cls(**kwargs)
        return obj


class DocumentAsViewMixin:

    @classmethod
    def _get_collection_name(cls):
        return cls.__name__

    @classmethod
    def _get_patch_query(cls) -> firestore.Query:
        collection_group_id = "_PATCH_{}" \
            .format(cls._get_collection_name())
        collection_group_query = CTX.db.collection_group(collection_group_id)
        return collection_group_query

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Should override in subclass
        :param args:
        :param kwargs:
        :return:
        """
        return super().new(*args, **kwargs)

    def _notify(self):
        """Once this object has a different value for underlying domain models,
                save the object to Firestore. Note that this method is
                expected to be called only after the data is consistent.
                (Ex. When all relevant changes made in a single transaction
                    from another server has been loaded into the object.
                )

        :return:
        """
        self.save()


class DocumentAsView(DocumentAsViewMixin,
                     ViewModelMixin,
                     PersistableMixin,
                     ReferencedObject):
    """
    Base for a view model intended to be read and modified as
        documents or collections in Firestore
    """
    pass


# def default_mapper(path_str_template: str, _kwargs):
#     """
#
#     :param path_str_template: example "company/{}"
#     :param args: example ["users"]
#     :return: DocumentReference for "company/users"
#     """
#     """
#     Maps a list of arguments from flask.View().get(args) to
#         a firestore reference that is used to construct
#         the ReferencedObject document
#     :return:
#     """
#     path_str = path_str_template.format(**_kwargs)
#     path = CTX.db.document(path_str)
#     return path
