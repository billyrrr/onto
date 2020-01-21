from collections import UserDict


class Struct(UserDict):

    def __init__(self, schema_obj):
        super().__init__()
        self.schema_obj = schema_obj

    @property
    def vals(self):
        for _, val in self.data.items():
            if isinstance(val, dict):
                for _, v in val.items():
                    yield v
            else:
                yield val

    def __getitem__(self, key):
        """
        Initializes a field to dict if it was not declared before

        :param item:
        :return:
        """

        if key not in self.data.keys():
            self.data[key] = dict()
        return super().__getitem__(key)

