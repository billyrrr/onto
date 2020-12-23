def test_get_variables():

    class A:

        def __init__(self, a: str):
            self.a = a

        def normal_f(self):
            return f"normal a evaluates to {self.a}"

    import inspect
    # NOTE: getclosurevars has bugs that are still not fixed yet
    # https://stackoverflow.com/questions/61964532/inspect-getclosurevars-classifies-attributes-as-global-or-unbound-how-to-distin
    v = inspect.getclosurevars(A.normal_f)
