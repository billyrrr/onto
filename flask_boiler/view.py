from .view_model import ViewModel


class FlaskAsView(ViewModel):
    pass

class DocumentAsView(ViewModel):
    pass


class DocumentAsViewMixin:

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Should override in subclass
        :param args:
        :param kwargs:
        :return:
        """
        return super().new(*args, **kwargs)

    def _notify(self):
        """Once this object has a different value for underlying domain models,
                save the object to Firestore. Note that this method is
                expected to be called only after the data is consistent.
                (Ex. When all relevant changes made in a single transaction
                    from another server has been loaded into the object.
                )

        :return:
        """
        self.save()


# def default_mapper(path_str_template: str, _kwargs):
#     """
#
#     :param path_str_template: example "company/{}"
#     :param args: example ["users"]
#     :return: DocumentReference for "company/users"
#     """
#     """
#     Maps a list of arguments from flask.View().get(args) to
#         a firestore reference that is used to construct
#         the ReferencedObject document
#     :return:
#     """
#     path_str = path_str_template.format(**_kwargs)
#     path = CTX.db.document(path_str)
#     return path
