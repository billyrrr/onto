from flask_boiler.primary_object import PrimaryObject


class DomainModel(PrimaryObject):
    """
    Domain model is intended for handling business logic.
    """

    @classmethod
    def _datastore(cls):
        from flask_boiler.context import Context as CTX
        return CTX.db


