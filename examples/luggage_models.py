from src import serializable, schema, fields, domain_model, view_model

Schema = schema.Schema


class LuggageItemSchema(Schema):
    luggage_type = fields.Str(load_from="luggage_type", dump_to="luggage_type")
    weight_in_lbs = fields.Integer(load_from="weight_in_lbs", dump_to="weight_in_lbs")
    # owner_id = fields.Str(
    #     load_from="owner_id",
    #     dump_to="owner_id",
    #     required=False)


class LuggageCollectionSchema(Schema):
    luggages = fields.Raw(many=True, load_from="luggages", dump_to="luggages")
    total_count = fields.Integer(dump_to="total_count", dump_only=True)
    total_weight = fields.Integer(dump_to="total_weight", dump_only=True)


class LuggageItem(domain_model.DomainModel):

    _schema_cls = LuggageItemSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.luggage_type = str()
        self.weight_in_lbs = int()
        self.owner_id = str()


class Luggages(view_model.ViewModel):
    """ Keeps track of luggage amount
    """

    _schema_cls = LuggageCollectionSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._luggage_d = dict()

    def get_update_func(self, dm_cls, *args, **kwargs):
        def update_func(*, vm, dm: dm_cls):
            vm.set(dm.doc_id, dm)
        return update_func

    @property
    def luggages(self):
        return [ v for _, v in self._luggage_d.items() ]

    @luggages.setter
    def luggages(self, val):
        for item in val:
            self._luggage_d[ item.luggage_id ] = item

    @property
    def total_weight(self) -> int:
        return self._get_weight()

    @property
    def total_count(self) -> int:
        return self._get_count()

    def set(self, luggage_id: str, luggage: LuggageItem):
        """ Sets a luggage associated with the luggage_id

        :param luggage_id:
        :param luggage:
        :return:
        """
        self._luggage_d[luggage_id] = luggage

    def _get_count(self) -> int:
        """ Returns the count for luggages by counting all luggages in self._luggage_list.

        :return:
        """
        return len(self._luggage_d)

    def _get_weight(self) -> int:
        """ Returns the weight for luggages by accumulating all luggages in self._luggage_list.

        :return:
        """
        weight = 0

        for key, item in self._luggage_d.items():
            weight += item.weight_in_lbs

        return weight


