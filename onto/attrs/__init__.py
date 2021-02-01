from collections import namedtuple
#
# def bproperty(*args, **kwargs):
#     from .attribute import PropertyAttribute
#     from pony.orm.core import Required
#     class C(Required, PropertyAttribute):
#         pass
#         # def __init__(self, *args, **kwargs):
#         #     super().__init__(str, *args, **kwargs)
#     return C(str, *args, **kwargs)


from .attribute import AttributeBase, \
    RelationshipAttribute as relation, \
    PropertyAttribute as bproperty, \
    DictAttribute as bdict, \
    EmbeddedAttribute as embed, \
    ObjectTypeAttribute as object_type, \
    LocalTimeAttribute as local_time, \
    StringAttribute as string, \
    PropertyAttribute as integer, \
    DocRefAttribute as doc_ref, \
    PropertyAttribute as action

from .attribute_new import AttributeBase
with AttributeBase._get_root() as attrs:
    attrs = attrs

# TODO: change import for string and integer
