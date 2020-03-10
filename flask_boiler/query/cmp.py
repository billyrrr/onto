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

    def __init__(self, fieldname):
        self.fieldname = fieldname
        self.constraints = list()

    def __lt__(self, other):
        self.constraints.append(("<", other))
        return self

    def __le__(self, other):
        self.constraints.append(("<=", other))
        return self

    def __gt__(self, other):
        self.constraints.append((">", other))
        return self

    def __ge__(self, other):
        self.constraints.append((">=", other))
        return self

    def __eq__(self, other):
        self.constraints.append(("==", other))
        return self

    def __ne__(self, other):
        raise ValueError("Not equal is not supported for Firestore")

    def has(self, item):
        """
        Maps to array membership "in"
        (needs to be reversed)

        :param item:
        :return:
        """
        self.constraints.append(("_in", item))
        return self


v = CMP()
