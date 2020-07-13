from collections import namedtuple

from .attribute import AttributeBase, \
    PropertyAttribute as bproperty, \
    RelationshipAttribute as relation, \
    DictAttribute as bdict, \
    EmbeddedAttribute as embed, \
    ObjectTypeAttribute as object_type, \
    LocalTimeAttribute as local_time, \
    PropertyAttribute as string, \
    PropertyAttribute as integer, \
    DocRefAttribute as doc_ref

# TODO: change import for string and integer
