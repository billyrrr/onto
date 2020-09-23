import unittest

from onto.database.firestore import FirestoreDatabase
from onto.query import cmp


class MyTestCase(unittest.TestCase):

    def test_eq(self):
        a = cmp.CMP().age
        b = a == 1
        assert isinstance(b, cmp.NodeCondition)
        assert b.constraints == [(FirestoreDatabase.Comparators.eq, 1)]

    def test_range(self):
        a = cmp.CMP().age
        b = 0 <= a <= 1
        assert isinstance(b, cmp.NodeCondition)
        assert b.constraints == [(FirestoreDatabase.Comparators.ge, 0), (FirestoreDatabase.Comparators.le, 1)]

    def test_excl_range(self):
        a = cmp.CMP().day
        b = 0 < a < 8
        assert isinstance(b, cmp.NodeCondition)
        assert b.constraints == [(FirestoreDatabase.Comparators.gt, 0), (FirestoreDatabase.Comparators.lt, 8)]

    def test_neq_raise(self):
        a = cmp.CMP().day

        def p():
            _ = a != 5

        self.assertRaises(ValueError, p)

    def test_in(self):
        a = cmp.CMP().friends
        assert isinstance(a, cmp.RootCondition)
        b = a.has("user_k")
        assert isinstance(b, cmp.NodeCondition)
        assert b.constraints == [(FirestoreDatabase.Comparators.contains, "user_k")]


if __name__ == '__main__':
    unittest.main()
