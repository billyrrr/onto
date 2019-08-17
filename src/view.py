from flasgger import SwaggerView
from .view_model import ViewModel
from google.cloud import firestore


class GenericView(SwaggerView):

    _view_model_cls = None
    # responses = dict()

    def __new__(cls, view_model_cls: ViewModel=None, description=None, *args, **kwargs):
        """
        TODO: test
        Note that this implementation is unstable.

        :param view_model_cls:
        :param args:
        :param kwargs:
        :return:
        """

        instance = super().__new__(cls)

        cls._view_model_cls = view_model_cls

        # cls.responses = {
        #     200: {
        #         "description": str() if description is None else description,
        #         "schema": cls._view_model_cls.schema_cls
        #     }
        # }

        return instance

    def get(self, dev_path):

        doc_ref: firestore.DocumentReference = \
            firestore.DocumentReference(dev_path)

        assert callable(self._view_model_cls)

        view_model_obj = self._view_model_cls(doc_ref=doc_ref)

        assert isinstance(view_model_obj, ViewModel)

        return view_model_obj.to_dict()
