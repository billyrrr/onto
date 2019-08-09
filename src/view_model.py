import warnings
from typing import List, Dict

from marshmallow import MarshalResult

from src.domain_model import DomainModel
from src.schema import generate_schema


class ViewModel(object):

    _fields = None
    _schema = None

    def __init_subclass__(cls, serializable_fields=None, **kwargs):
        """
        See: https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        :param serializable_fields:
        :param kwargs:
        :return:
        """
        super().__init_subclass__(**kwargs)

        # if serializable_fields is None:
        #     # raise ValueError("Serializable fields needs"
        #     #                  "to be specified. Eg. "
        #     #                  "class SubclassOfViewModel("
        #     #                  "ViewModel, serializable_fields=['property_a'])")
        #     cls._fields = list()
        # else:
        #

        cls._fields = serializable_fields

        cls._schema = generate_schema(cls)

    @classmethod
    def _infer_fields(cls) -> list:
        res = list()

        def is_private_var_name(var_name):
            if len(var_name) == 0:
                raise ValueError
            else:
                return var_name[0] == "_"

        for key, val in cls.__dict__.items():
            if not is_private_var_name(key):
                res.append(key)

        return res


    @classmethod
    def get_fields(cls) -> list:
        """
        Returns a list of fields that are serialized and deserialized.

        :return:
        """

        if cls._fields is None:
            warnings.warn("Inferring fields to serialize and deserialize "
                          "by variable name. "
                          "serializable_fields should rather " +
                          "be specified. Eg. " +
                          "class SubclassOfViewModel(" +
                          "ViewModel, serializable_fields=['property_a'])")
            return cls._infer_fields()
        else:
            return cls._fields

    def __new__(cls, *args, **kwargs):

        instance = super().__new__(cls, *args, **kwargs)
        return instance

    def __init__(self):
        self.business_properties: Dict[str, DomainModel] = dict()

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data
