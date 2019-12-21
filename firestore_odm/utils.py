import random
import string
from typing import TypeVar


# Generate a random string
# with 32 characters.
# https://www.geeksforgeeks.org/generating-random-ids-python/
from functools import partial

from google.cloud.firestore import DocumentSnapshot
from inflection import camelize, underscore

from .model_registry import ModelRegistry


def random_id():
    random_id_str = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    return random_id_str


def obj_type_serialize(obj: object):
    """ Returns class name. To be used with Schema.obj_type field.

    :param obj:
    :return:
    """

    return obj.__class__.__name__


def obj_type_deserialize(value):
    """ Returns class name. To be used with Schema.obj_type field.

    :param value:
    :return:
    """

    return value


def attr_name_to_firestore_key(s):
    res = camelize(s, uppercase_first_letter=False)
    if firestore_key_to_attr_name(res) != s:
        raise ValueError("attr_name: {} is not invertible. "
                         .format(s)
                         )
    else:
        return res


firestore_key_to_attr_name = underscore


T = TypeVar('T', covariant=True)


def snapshot_to_obj(
        snapshot: DocumentSnapshot,
        super_cls: T = None) -> T:
    """ Converts a firestore document snapshot to FirestoreObject

    :param snapshot: firestore document snapshot
    :param super_cls: subclass of FirestoreObject
    :return:
    """

    if not snapshot.exists:
        return None

    d = snapshot.to_dict()
    obj_type = d["obj_type"]
    obj_cls = ModelRegistry.get_cls_from_name(obj_type)

    if obj_cls is None:
        raise ValueError("Cannot read obj_type: {}. "
                         "Make sure that obj_type is a subclass of {}. "
                         .format(obj_type, super_cls))

    if super_cls is not None:
        assert issubclass(obj_cls, super_cls)

    obj = obj_cls.from_dict(d=d, doc_ref=snapshot.reference)
    return obj
