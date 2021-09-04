import threading

# from google.cloud.firestore import DocumentReference

from .collection_mixin import CollectionMixin, CollectionMemberMeta
from .context import Context as CTX
from .models.base import Serializable
from .utils import random_id


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

    def __get_ref(self) -> 'google.cloud.firestore.DocumentReference':
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
    def get(cls, store=None, once=False, **kwargs):
        """ Returns an instance of view model with listener activated.

        :param struct_d: Binding structure.
        :param once: If set to True, do not listen to future document updates
        :return:
        """

        obj = cls.new(store=store, **kwargs)
        return obj

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
            self, f_notify=None, store=None, *args, **kwargs):
        """

        :param f_notify: callback to notify that view model's
            business properties have finished updating
        :param args:
        :param kwargs:
        """
        self.store = store
        super().__init__(*args, **kwargs)
        self.f_notify = f_notify

        self.has_first_success = False
        self.success_condition = threading.Condition()
        self._notify()

    def propagate_change(self):
        """ Save all objects mutated in a mutation

        :return:
        """
        self.store.propagate_back()

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

    def _notify(self):
        """ Notify that this object has been changed by underlying view models.
            Once this object has a different value for underlying domain models,
                save the object to Firestore. Note that this method is
                expected to be called only after the data is consistent.
                (Ex. When all relevant changes made in a single transaction
                    from another server has been loaded into the object.
                )
            NOTE: if f_notify is not set has_first_success will still
                be set to True, and wait_for_first_success() will return
                exactly after _notify is called (which is empty).
        """
        if self.f_notify is not None:
            self.f_notify(obj=self)
        with self.success_condition:
            self.success_condition.notify()
            self.has_first_success = True

    def to_view_dict(self):
        # with self.lock:
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


class ViewModel(ViewModelMixin, Serializable):
    """ View model are generated and refreshed automatically as domain
            model changes. Note that states stored in ViewModel
            are unreliable and should not be used to evaluate other states.
            Note that since ViewModel is designed to store in a database
            that is not strongly consistent, fields may be inconsistent.

    """
    pass
    # def __init__(self, *args, doc_ref=None, **kwargs):
    #     super().__init__(*args, doc_ref=doc_ref, **kwargs)


class ViewModelR(
    CollectionMixin, ViewModel, metaclass=CollectionMemberMeta):
    """
    ViewModelR = View Model with Repo
    """

    @classmethod
    def _datastore(cls):
        return CTX.db

    @classmethod
    def _get_collection(cls):
        return cls._datastore().ref / "**" / cls._get_collection_name()