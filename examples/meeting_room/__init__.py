from onto.context import Context as CTX
if CTX.config is None:
    CTX.load()

from . import view_models
from . import domain_models
