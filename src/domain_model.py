from typing import Callable

from .firestore_object import PrimaryObject


class DomainModel(PrimaryObject):
    """
    Domain model is intended for handling business logic.
    """
    pass

    @classmethod
    def get_update_func(cls, obj_type, *args, **kwargs) -> Callable:
        """ Returns a function for updating a view
        """
        raise NotImplementedError
