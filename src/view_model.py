from typing import Dict, Tuple, Callable

from google.cloud.firestore import DocumentReference
from marshmallow import MarshalResult

from .domain_model import DomainModel
from .firestore_object import ReferencedObject
from .serializable import Serializable

from src.context import Context as CTX


class ViewModel(ReferencedObject):
    """
    TODO: check if unsubscribe needs to be called on all on_update functions
            when deleting an instance.
    TODO: consider redundancy when ViewModel object becomes invalid in runtime
    TODO: consider decoupling bind_to to a superclass
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.business_properties: Dict[str, Tuple[str, DomainModel, Callable]] = dict()
        self._on_update_funcs: Dict[str, Callable] = dict()

    def bind_to(self, key, domain_model_id, obj, update_function):
        """
        Do not destruct obj passed into this method for now
            (this impl should only be temporary)
        :param key:
        :param domain_model_id:
        :param obj: (DO NOT DESTRUCT)
        :param update_function:
        :return:
        """

        self.business_properties[key] = (domain_model_id, obj, update_function)

        update_function(self, obj)

        if key in self._on_update_funcs:
            # Release the previous on_snapshot functions
            #   https://firebase.google.com/docs/firestore/query-data/listen
            f = self._on_update_funcs[key]

            f.unsubscribe()

        dm_id, dm, upd_func = self.business_properties[key]

        def on_update(docs, changes, readtime):
            # do something with this ViewModel

            assert len(docs) == 1

            doc = docs[0]
            updated_dm = dm.__class__.create(dm_id)
            updated_dm._import_properties(doc.to_dict())

            self.business_properties[key] = (dm_id, updated_dm, upd_func)

            upd_func(self, updated_dm)

            self.save()

        self._on_update_funcs[key] = on_update
        dm_ref: DocumentReference = dm.doc_ref
        dm_ref.on_snapshot(on_update)

    def to_dict(self):
        # TODO: delete
        mres: MarshalResult = self.schema_obj.dump(self)
        return mres.data

