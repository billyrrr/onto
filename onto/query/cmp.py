"""
DELICATE: implementation depends on magic; make changes carefully
Interface was inspired by public API of RethinkDB.
RethinkDB is released under apache 2.0 license.
"""


class CMP:

    def __getattr__(self, item):
        cond = RootCondition()
        from onto.context import Context as CTX
        cond.comparator_cls = CTX.db.Comparators
        cond.attr_name = item
        return cond


class Condition:
    """
    Maps <, <=, ==, >=, >, and in to python comparator.
    See test_query for usage
    """

    @property
    def comparator_cls(self):
        return self._comparator_cls

    @comparator_cls.setter
    def comparator_cls(self, value):
        self._comparator_cls = value

    @property
    def attr_name(self):
        return self._attr_name

    @attr_name.setter
    def attr_name(self, value):
        self._attr_name = value

    def _constraint_for(self, other, opname):
        op = getattr(self.comparator_cls, opname)
        return [*self.constraints, (op, other)]

    def __and__(self, other):
        return super().__and__(self, other)

    def __iand__(self, other):
        return super().__iand__(self, other)

    # def __bool__(self):
    #     """
    #     So that __and__ is triggered;
    #     Note that this affects __or__
    #     :return:
    #     """
    #     return False


class RootCondition(Condition):

    def __init__(self, *args, attr_name=None, comparator_cls=None, **kwargs):
        self.attr_name = attr_name
        self.comparator_cls = comparator_cls
        super().__init__(*args, **kwargs)

    def __lt__(self, other):
        return self._descendant(constraints=self._constraint_for(other, 'lt'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __le__(self, other):
        return self._descendant(constraints=self._constraint_for(other, 'le'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __gt__(self, other):
        return self._descendant(constraints=self._constraint_for(other, 'gt'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __ge__(self, other):
        return self._descendant(constraints=self._constraint_for(other, 'ge'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __eq__(self, other):
        return self._descendant(constraints=self._constraint_for(other, 'eq'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    # def __bool__(self):
    #     """
    #     So that __and__ is triggered;
    #     Note that this affects __or__
    #     :return:
    #     """
    #     return True
    #
    # def __and__(self, other):
    #     return self._descendant(constraints=[*self.constraints, *other.constraints], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __ne__(self, other):
        raise ValueError("Not equal is not supported for Firestore")

    def has(self, item):
        """
        Maps to array membership "in"
        (needs to be reversed)

        :param item:
        :return:
        """
        return self._descendant(constraints=self._constraint_for(item, 'contains'), comparator_cls=self.comparator_cls, attr_name=self.attr_name)


    @property
    def _descendant(self):
        return NodeCondition

    @property
    def constraints(self):
        return []

    @Condition.comparator_cls.getter
    def comparator_cls(self):
        if self._comparator_cls is None:
            return self.parent._datastore().Comparators
        else:
            return self._comparator_cls

    @Condition.attr_name.getter
    def attr_name(self):
        if self._attr_name is None:
            return self.name
        else:
            return self._attr_name


class NodeCondition(Condition):

    @property
    def _descendant(self):
        return NodeCondition

    def __init__(self, *args, constraints=None, comparator_cls=None, attr_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.constraints = constraints
        self.comparator_cls = comparator_cls  # This calls setter in superclass
        self.attr_name = attr_name  # This calls setter in superclass

    def __lt__(self, other):
        self.constraints = self._constraint_for(other, 'lt')
        return self

    def __le__(self, other):
        self.constraints = self._constraint_for(other, 'le')
        return self

    def __gt__(self, other):
        self.constraints = self._constraint_for(other, 'gt')
        return self

    def __ge__(self, other):
        self.constraints = self._constraint_for(other, 'ge')
        return self

    def __eq__(self, other):
        self.constraints = self._constraint_for(other, 'eq')
        return self

    # #
    # def __and__(self, other):
    #     self._descendant(constraints=[*self.constraints, *other.constraints], comparator_cls=self.comparator_cls, attr_name=self.attr_name)

    def __ne__(self, other):
        raise ValueError("Not equal is not supported for Firestore")

    def has(self, item):
        """
        Maps to array membership "in"
        (needs to be reversed)

        :param item:
        :return:
        """
        self.constraints = self._constraint_for(item, 'contains')
        return self


v = CMP()
