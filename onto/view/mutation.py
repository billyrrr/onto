from onto.models.mixin import Importable, Exportable, NewMixin
from onto.models.base import BaseRegisteredModel, Schemed
from onto.view_model import ViewModel, ViewModelMixin


class Mutation(BaseRegisteredModel,
               Schemed, Importable, NewMixin, Exportable):

    view_model_cls = None


class PatchMutation(Mutation):

    def __init__(self):
        super().__init__()

    # @classmethod
    # def mutate_create(cls, doc_id=None, data=None):
    #     obj = cls.domain_model_cls.new(
    #         doc_id=doc_id,
    #         with_dict=data)
    #     obj.save()

    @classmethod
    def mutate_patch(cls, doc_id=None, data=None):
        obj = cls.view_model_cls.get(doc_id=doc_id)
        assert isinstance(obj, ViewModelMixin)
        obj.update_vals(with_dict=data)
        obj.propagate_change()

    @classmethod
    def mutate_patch_one(cls, obj=None, data=None):
        if data:
            assert isinstance(obj, ViewModelMixin)
            obj.update_vals(with_dict=data)
            obj.propagate_change()
