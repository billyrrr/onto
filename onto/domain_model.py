from onto.primary_object import PrimaryObject


class DomainModel(PrimaryObject):
    """
    Domain model is intended for handling business logic.
    """

    @classmethod
    def _datastore(cls):
        from onto.context import Context as CTX
        return CTX.db


