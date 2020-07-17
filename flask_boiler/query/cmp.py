"""
Interface was inspired by public API of RethinkDB.
RethinkDB is released under apache 2.0 license.
"""


class CMP:

    def __getattr__(self, item):
        return Condition(fieldname=item)


class Condition:
    """
    Maps <, <=, ==, >=, >, and in to python comparator.
    See test_query for usage
    """

    def __init__(self, *args, constraints=None, comparator_cls=None, attr_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if constraints is None:
            constraints = list()
        self.constraints = constraints
        self._comparator_cls = comparator_cls
        self._attr_name = attr_name

    @property
    def comparator_cls(self):
        if self._comparator_cls is None:
            return self.parent._datastore().Comparators
        else:
            return self._comparator_cls

    @property
    def attr_name(self):
        if self._attr_name is None:
            return self.name
        else:
            return self._attr_name

    def __lt__(self, other):
        return Condition(constraints=self.constraints+[(self.comparator_cls.lt, other)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __le__(self, other):
        return Condition(constraints=self.constraints+[(self.comparator_cls.le, other)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __gt__(self, other):
        return Condition(constraints=self.constraints+[(self.comparator_cls.gt, other)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __ge__(self, other):
        return Condition(constraints=self.constraints+[(self.comparator_cls.ge, other)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __eq__(self, other):
        return Condition(constraints=self.constraints+[(self.comparator_cls.eq, other)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __ne__(self, other):
        raise ValueError("Not equal is not supported for Firestore")

    def has(self, item):
        """
        Maps to array membership "in"
        (needs to be reversed)

        :param item:
        :return:
        """
        return Condition(constraints=self.constraints+[(self.comparator_cls.contains, item)], comparator_cls=self.comparator_cls, attr_name=self.attr_name)


v = CMP()
