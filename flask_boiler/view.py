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

    def new(cls, *args, **kwargs):
        raise NotImplementedError

    def get_on_update(self,
                  dm_cls=None, dm_doc_id=None,
                  update_func=None, key=None):
        # do something with this ViewModel

        def __on_update(dm: DomainModel):

            update_func(vm=self, dm=dm)

            self.business_properties[key] = dm

        def _on_update(docs, changes, readtime):
            if len(docs) == 0:
                # NO CHANGE
                return
            elif len(docs) != 1:
                raise NotImplementedError
            doc = docs[0]
            updated_dm = dm_cls.create(doc_id=dm_doc_id)
            updated_dm._import_properties(doc.to_dict())
            __on_update(updated_dm)

        return _on_update

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
    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj


class DocumentAsViewMixin:

    def new(cls, *args, **kwargs):
        raise NotImplementedError

    def _notify(self):
        """ Notify that this object has been changed by underlying view models

        :return:
        """
        self.save()


class DocumentAsView(DocumentAsViewMixin,
                     ViewModelMixin,
                     PersistableMixin,
                     ReferencedObject):
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
