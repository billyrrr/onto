from collections import namedtuple


RelationshipReference = namedtuple(
    "RelationshipReference",
    ['doc_ref', 'nested', 'obj'],
    defaults=(None, None, None,)
)

EmbeddedElement = namedtuple(
    "EmbeddedElement",
    ['d', 'obj'],
    defaults=(None, None)
)
