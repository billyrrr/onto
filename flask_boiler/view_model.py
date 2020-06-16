import threading
from typing import Dict, Tuple, Callable

from dictdiffer import diff, patch
from google.cloud.firestore import DocumentReference

from flask_boiler.business_property_store import BusinessPropertyStore, to_ref
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.watch import DataListener
from .context import Context as CTX
from .domain_model import DomainModel
from flask_boiler.referenced_object import ReferencedObject
from .models.base import Serializable
from .struct import Struct
from .business_property_store import BPSchema
from .utils import random_id, snapshot_to_obj


class PersistableMixin:
    _struct_collection_id = "Persistable"

    def __init__(self, *args, struct_id=None, struct_d=None, **kwargs):
        super().__init__(*args, **kwargs)
        if struct_id is None:
            self._structure_id = random_id()
        else:
            self._structure_id = struct_id

        if struct_d is None:
            self._structure = dict()
        else:
            self._structure = struct_d
        # self._structure["vm_type"] = self.__class__.__name__

    def __get_ref(self) -> DocumentReference:
        return CTX.db.collection(self._struct_collection_id) \
            .document(self._structure_id)

    def _save__structure(self):
        self.__get_ref().set(self._structure)

    def _get__structure(self):
        return self.__get_ref().get()


class ViewModelMixin:
    """
    TODO: check if unsubscribe needs to be called on all on_update functions
            when deleting an instance.
    TODO: consider redundancy when ViewModel object becomes invalid in runtime
    TODO: consider decoupling bind_to to a superclass
    """

    @classmethod
    def get(cls, struct_d=None, once=False, **kwargs):
        """ Returns an instance of view model with listener activated.

        :param struct_d: Binding structure.
        :param once: If set to True, do not listen to future document updates
        :return:
        """
        obj = cls(struct_d=struct_d, **kwargs)
        obj.bind_all()

        if once:
            obj.listen_once()
        else:
            obj.listen()
        return obj

    def bind_all(self):

        for obj_type, doc_id in self._struct_d.vals:
            self.__subscribe_to(
                dm_cls=obj_type,
                dm_doc_id=doc_id,
            )

    @classmethod
    def get_many(cls, struct_d_iterable=None, once=False):
        """ Gets a list of view models from a list of
            binding structures.

        :param struct_d_iterable: Binding structure.
        :param once: If set to True, do not listen to future document updates
        :return:
        """
        return [cls.get(struct_d=struct_d, once=once)
                for struct_d in struct_d_iterable]

    def __init__(
            self, struct_d=None, f_notify=None, store=None, *args, **kwargs):
        """

        :param f_notify: callback to notify that view model's
            business properties have finished updating
        :param args:
        :param kwargs:
        """
        if store is None:
            self.snapshot_container = SnapshotContainer()
            if struct_d is None:
                struct_d = Struct(BPSchema())
            self._struct_d = struct_d
            self.store = BusinessPropertyStore(
                struct=self._struct_d,
                snapshot_container=self.snapshot_container)
        else:
            self.store = store
        super().__init__(*args, **kwargs)
        self._on_update_funcs: Dict[str, Tuple] = dict()
        self.listener = None
        self.f_notify = f_notify
        self.lock = threading.Lock()

        self.has_first_success = False
        self.success_condition = threading.Condition()

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

        self._struct_d[key] = (obj_type, doc_id)

        self.__subscribe_to(
            dm_cls=obj_type,
            dm_doc_id=doc_id,
        )

    def get_on_update(self,
                      dm_cls=None, dm_doc_id=None, dm_doc_ref_str=None):
        # do something with this ViewModel

        def _on_update(docs, changes, readtime):
            try:
                if len(docs) == 0:
                    # NO CHANGE
                    return
                elif len(docs) != 1:
                    raise NotImplementedError
                doc = docs[0]

                self.snapshot_container.set(to_ref(dm_cls, dm_doc_id), doc)
            except Exception as e:
                CTX.logger.exception(f"Error encountered when updating"
                                     f" {docs[0].reference._path} "
                                     f"for {dm_cls, dm_doc_id}")

        return _on_update

    def propagate_change(self):
        """ Save all objects mutated in a mutation

        :return:
        """
        raise NotImplementedError

    def __subscribe_to(self, *, dm_cls, dm_doc_id):
        """

        :param dm_cls:
        :param dm_doc_id:
        :return:
        """

        """
        if key in self._on_update_funcs:
            # Release the previous on_snapshot functions
            #   https://firebase.google.com/docs/firestore/query-data/listen
            f, doc_watch = self._on_update_funcs[key]
            # TODO: add back, see:
            # https://github.com/googleapis/google-cloud-python/issues/9008
            # https://github.com/googleapis/google-cloud-python/issues/7826
            # doc_watch.unsubscribe()
        """

        dm_ref: DocumentReference = dm_cls._get_collection().document(
            dm_doc_id)
        on_update = self.get_on_update(
            dm_cls=dm_cls, dm_doc_id=dm_doc_id,
            dm_doc_ref_str=dm_ref._document_path,
        )
        # doc_watch = dm_ref.on_snapshot(on_update)
        self._on_update_funcs[dm_ref._document_path] = on_update

    # def diff(self, new_state, allowed=None):
    #     prev_state = self.to_view_dict()
    #
    #     if prev_state["lastName"] == "Manes" and new_state["lastName"] == "M.":
    #         return {
    #             "lastName": "M."
    #         }
    #     else:
    #         return dict()
    #
    #     if allowed is not None:
    #         prev_state = {key: val
    #                       for key, val in prev_state.items()
    #                       if key in allowed}
    #         new_state = {key: val
    #                      for key, val in new_state.items()
    #                      if key in allowed}
    #
    #     diff_res = diff(prev_state, new_state)
    #     result = patch(diff_result=diff_res,
    #                    destination=dict(),
    #                    in_place=False
    #                    )
    #     return result

    def _snapshot_callback(self, docs, changes, read_time):
        """
        docs (List(DocumentSnapshot)): A callback that returns the
                    ordered list of documents stored in this snapshot.
        changes (List(str)): A callback that returns the list of
                    changed documents since the last snapshot delivered for
                    this watch.
        read_time (string): The ISO 8601 time at which this
                    snapshot was obtained.
        :return:
        """

        with self.snapshot_container.lock:
            n = len(docs)
            for i in range(n):
                doc = docs[i]

                on_update = self._on_update_funcs[doc.reference._document_path]
                # TODO: restore parameter "changes"
                on_update([doc], None, read_time)

        with self.snapshot_container.lock, self.lock:
            self.store.refresh()

        with self.lock:
            self._invoke_vm_callbacks()

        # Note: technically this can go wrong as it can read the value from
        #   the next refresh
        # TODO: fix a bug where success_condition keeps waiting when this line
        #   fails with exception
        self._notify()

        with self.success_condition:
            if not self.has_first_success:
                self.has_first_success = True
                self.success_condition.notify_all()

    def wait_for_first_success(self):
        """ Blocks a thread until self.has_first_success is True.
        TODO: fix a bug where error may arise when a prior task crashes
            with an exception and the code here keeps waiting for
            self.has_first_success to become true and blocks the thread
            from executing the next task
        NOTE: the above-said behaviors happen when using self._notify
        :return:
        """
        with self.success_condition:
            while not self.has_first_success:
                self.success_condition.wait()

    def listen_once(self):
        """ Retrieves domain models binded to a view model in an async
                operation and disconnects the listener once the data
                is retrieved so that no future updates to the domain
                models are processed.
        """
        self.listener = DataListener(
            [dm_ref for dm_ref in self._on_update_funcs],
            snapshot_callback=self._snapshot_callback,
            firestore=CTX.db,
            once=True
        )

        self.wait_for_first_success()

    def listen(self):
        """ Listens to domain models binded to a view model in an async
                operation. Note that the domain models may not yet be retrieved
                after this function returns.
        """

        self.listener = DataListener(
            [dm_ref for dm_ref in self._on_update_funcs],
            snapshot_callback=self._snapshot_callback,
            firestore=CTX.db,
            once=False
        )

        self.wait_for_first_success()

    # def _refresh_business_property(self, ):
    #     with self.snapshot_container.lock:
    #         for key, val in self._structure.items():
    #             obj_type, doc_id = val
    #             snapshot = self.snapshot_container.get((obj_type, doc_id), )
    #             self.business_properties[key] = snapshot_to_obj(snapshot=snapshot)

    def _invoke_vm_callbacks(self):
        for key, val in self._struct_d.items():
            b = getattr(self.store, key)
            if isinstance(val, dict):
                for k, v in val.items():
                    obj_type, doc_id = v
                    vm_update_callback = self.get_vm_update_callback(
                        dm_cls=obj_type)
                    vm_update_callback(vm=self, dm=b[k])
            else:
                obj_type, doc_id = val
                vm_update_callback = self.get_vm_update_callback(
                    dm_cls=obj_type)
                vm_update_callback(vm=self, dm=b)

    def _notify(self):
        """ Notify that this object has been changed by underlying view models.
            Once this object has a different value for underlying domain models,
                save the object to Firestore. Note that this method is
                expected to be called only after the data is consistent.
                (Ex. When all relevant changes made in a single transaction
                    from another server has been loaded into the object.
                )
        """
        if self.f_notify is not None:
            self.f_notify(obj=self)

    def get_vm_update_callback(self, dm_cls, *args, **kwargs) -> Callable:
        """ Returns a function for updating a view
        """

        def default_to_do_nothing(vm: ViewModel, dm: DomainModel):
            pass

        return default_to_do_nothing

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

    def to_view_dict(self):
        with self.lock:
            return self._export_as_dict()

    # def _export_as_dict(self, *args, transaction=None, **kwargs):
    #     """ Must not modify datastore
    #
    #     :param args:
    #     :param transaction:
    #     :param kwargs:
    #     :return:
    #     """
    #     return self._export_as_view_dict(*args, **kwargs)

    def to_dict(self):
        return self.to_view_dict()


class ViewModel(ViewModelMixin, ReferencedObject):
    """ View model are generated and refreshed automatically as domain
            model changes. Note that states stored in ViewModel
            are unreliable and should not be used to evaluate other states.
            Note that since ViewModel is designed to store in a database
            that is not strongly consistent, fields may be inconsistent.

    """

    def __init__(self, *args, doc_ref=None, **kwargs):
        super().__init__(*args, doc_ref=doc_ref, **kwargs)
