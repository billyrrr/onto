
class Identifiable:
    pass


class Entity(Identifiable):
    pass


class ValueObject:
    pass


class Aggregate(Identifiable):

    class Meta:
        is_root = False


class DomainService:
    """
    Stateless
    """
    pass


class WeakReference:
    pass


class StrongReference:
    pass


class ApplicationService:
    pass


