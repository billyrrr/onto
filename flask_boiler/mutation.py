from flask_boiler.serializable import BaseRegisteredModel, Schemed, \
    Importable, NewMixin, AutoInitialized, Exportable


class Mutation(BaseRegisteredModel,
               Schemed, Importable, NewMixin, AutoInitialized, Exportable):

    domain_model_cls = None

    @classmethod
    def mutate_create(cls, doc_id=None, data=None):
        obj = cls.domain_model_cls.create(
            doc_id=doc_id,
            with_dict=data)
        obj.save()

    @classmethod
    def mutate_patch(cls, doc_id=None, data=None):
        obj = cls.domain_model_cls.get(doc_id=doc_id)
        obj.update_vals(with_dict=data)
        obj.save()
