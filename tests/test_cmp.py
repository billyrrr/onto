import unittest
from flask_boiler.query import cmp


class MyTestCase(unittest.TestCase):

    def test_eq(self):
        a = cmp.CMP().age
        assert isinstance(a, cmp.Condition)
        b = a == 1
        assert isinstance(b, cmp.Condition)
        assert b.constraints == [("==", 1)]
        assert b.fieldname == "age"

    def test_range(self):
        a = cmp.CMP().age
        assert isinstance(a, cmp.Condition)
        b = 0 <= a <= 1
        assert isinstance(b, cmp.Condition)
        assert b.constraints == [(">=", 0), ("<=", 1)]
        assert b.fieldname == "age"

    def test_excl_range(self):
        a = cmp.CMP().day
        assert isinstance(a, cmp.Condition)
        b = 0 < a < 8
        assert isinstance(b, cmp.Condition)
        assert b.constraints == [(">", 0), ("<", 8)]
        assert b.fieldname == "day"

    def test_neq_raise(self):
        a = cmp.CMP().day

        def p():
            _ = a != 5

        self.assertRaises(ValueError, p)

    def test_in(self):
        a = cmp.CMP().friends
        assert isinstance(a, cmp.Condition)
        b = a.has("user_k")
        assert isinstance(b, cmp.Condition)
        assert b.constraints == [("array_contains", "user_k")]
        assert b.fieldname == "friends"


if __name__ == '__main__':
    unittest.main()
