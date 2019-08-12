from marshmallow import Schema, MarshalResult

from src.schema import generate_schema
from src.serializable import Serializable
from src.firestore_object import FirestoreObject
from .context import Context as CTX
from .utils import random_id


class DomainModel(FirestoreObject):

    pass
