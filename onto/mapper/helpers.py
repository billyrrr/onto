from collections import namedtuple


RelationshipReference = namedtuple(
    "RelationshipReference",
    ['doc_ref', 'nested', 'obj', 'obj_type'],
    defaults=(None, None, None, None)
)

EmbeddedElement = namedtuple(
    "EmbeddedElement",
    ['d', 'obj_cls', 'obj'],
    defaults=(None, None, None)
)
