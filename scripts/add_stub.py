if __name__ == "__main__":

    from onto.attrs.unit import _ModelRegistry

    classnames = set(_ModelRegistry._REGISTRY.keys())

    import ast

    with open('onto/attrs/unit.py') as unit:
        tree = ast.parse(unit.read())


        def yield_elems():
            for elem in tree.body:
                if isinstance(elem, ast.ClassDef):
                    name = elem.name
                    if name in classnames:
                        yield elem

            else:
                yield from ()


        def get_init(elem: ast.ClassDef):
            init = None

            class CollectInit(ast.NodeVisitor):

                def visit_FunctionDef(self, node: ast.FunctionDef):
                    if node.name == '__init__':
                        nonlocal init
                        init = node

            CollectInit().visit(elem)

            return init


        with open('onto/attrs/attribute_new.py') as attribute_new:
            attribute_new_tree = ast.parse(attribute_new.read())
            attribute_new_class: ast.ClassDef = next(elem for elem in attribute_new_tree.body if
                                                     isinstance(elem, ast.ClassDef) and elem.name == 'AttributeBase')
            # attribute_new_clas

        for elem in yield_elems():
            init = get_init(elem)
            if init is None:
                continue
            from inflection import underscore

            name = underscore(elem.name)
            new_f = ast.FunctionDef(name=name, args=init.args, body=[ast.Pass()], decorator_list=[],
                                    returns=[ast.Constant(value='AttributeBase')])

            # f = ast.unparse(new_f)
            # print(f)

            attribute_new_class.body.append(
                new_f
            )

        with open("onto/attrs/attribute_new.pyi", 'w+') as io:
            attribute_new_tree = ast.fix_missing_locations(attribute_new_tree)
            ss = ast.unparse(attribute_new_tree)
            io.write(ss)
