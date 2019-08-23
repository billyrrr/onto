from typing import Dict, Tuple, Callable

from google.cloud.firestore import DocumentReference, Watch
from marshmallow import MarshalResult

from .domain_model import DomainModel
from .firestore_object import ReferencedObject, FirestoreObject
from .serializable import Serializable
from .utils import obj_type_deserialize, random_id

from .context import Context as CTX


class Persistable:
    _COLLECTION_ID = "Persistable"

    @staticmethod
    def _create__structure_id():
        return random_id()

    @staticmethod
    def __get_ref(structure_doc_id) -> DocumentReference:
        return CTX.db.collection(Persistable._COLLECTION_ID) \
            .document(structure_doc_id)

    @staticmethod
    def _save__structure(structure_doc_id, d):
        structure_doc_ref: DocumentReference = Persistable \
            .__get_ref(structure_doc_id)
        structure_doc_ref.set(d)

    @staticmethod
    def _get__structure(structure_doc_id):
        structure_doc_ref: DocumentReference = Persistable \
            .__get_ref(structure_doc_id)
        structure_doc_ref.get()


class ViewModel(ReferencedObject, Persistable):
    """ View model are generated and refreshed automatically
            as domain model changes.

    Note that states stored in ViewModel are unreliable and should
        not be used to evaluate other states.

    Note that since ViewModel is designed to store in a database that is not
        strongly consistent, fields may be inconsistent.


    TODO: check if unsubscribe needs to be called on all on_update functions
            when deleting an instance.
    TODO: consider redundancy when ViewModel object becomes invalid in runtime
    TODO: consider decoupling bind_to to a superclass
    """

    def __init__(self, struct_id=None, **kwargs):
        super().__init__(**kwargs)

        def init_struct():
            self._structure_id = self._create__structure_id()
            self._structure = dict()
            self._structure["vm_type"] = self.__class__.__name__
            self._save__structure(self._structure_id, self._structure)

        def get_struct(struct_id):
            self._structure_id = struct_id
            self._structure = self._get__structure(self._structure_id)
            self._save__structure(self._structure_id, self._structure)

        if struct_id is None:
            init_struct()
        else:
            get_struct(struct_id)

        self.business_properties: Dict[str, DomainModel] = dict()
        self._on_update_funcs: Dict[str, Tuple] = dict()

    def _bind_to_domain_model(self, *, key, obj_type, doc_id):
        """

        Note that ViewModel will change when first binded

        See: https://firebase.google.com/docs/firestore/query-data/listen
        "You can listen to a document with the onSnapshot() method.
            An initial call using the callback you provide creates a document
            snapshot immediately with the current contents of the single
            document. Then, each time the contents change, another call
            updates the document snapshot."

        :param key:
        :param obj_type:
        :param doc_id:
        :return:
        """
        obj_cls: DomainModel = Serializable.get_subclass_cls(obj_type)

        update_func = self.get_update_func(dm_cls=obj_cls)

        self._structure[key] = (obj_type, doc_id, update_func)
        self.__subscribe_to(
            key=key,
            dm_cls=obj_cls,
            update_func=update_func,
            dm_doc_id=doc_id
        )
        # _, doc_watch = self._on_update_funcs[key]
        # assert isinstance(doc_watch, Watch)

    def __subscribe_to(self, *, key, dm_cls, update_func,
                       dm_doc_id):

        if key in self._on_update_funcs:
            # Release the previous on_snapshot functions
            #   https://firebase.google.com/docs/firestore/query-data/listen
            f, doc_watch = self._on_update_funcs[key]

            doc_watch.unsubscribe()

        def on_update(docs, changes, readtime):
            # do something with this ViewModel

            assert len(docs) == 1

            doc = docs[0]
            updated_dm = dm_cls.create(doc_id=dm_doc_id)
            updated_dm._import_properties(doc.to_dict())
            update_func(vm=self, dm=updated_dm)

            self.business_properties[key] = updated_dm

            self.save()

        dm_ref: DocumentReference = dm_cls._get_collection().document(dm_doc_id)
        doc_watch = dm_ref.on_snapshot(on_update)
        self._on_update_funcs[key] = (on_update, doc_watch)

    def get_update_func(self, dm_cls, *args, **kwargs) -> Callable:
        """ Returns a function for updating a view
        """
        raise NotImplementedError

    def bind_to(self, key, obj_type, doc_id):
        """ Binds to a domain model so that this view model changes
                when such domain model changes.

        :param key:
        :param obj_type:
        :param doc_id:
        :return:
        """
        return self._bind_to_domain_model(
            key=key,
            obj_type=obj_type,
            doc_id=doc_id)

    @classmethod
    def get(cls, *args, **kwargs):
        raise NotImplementedError

    def to_view_dict(self):
        return self._export_as_view_dict()

    def to_dict(self):
        return self.to_view_dict()
