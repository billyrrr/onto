import pytest
from flasgger import SwaggerView, Swagger
from flask import Flask

from flask_boiler import schema, fields, view, domain_model, factory, \
    view_model, view_mediator

from .fixtures import CTX


@pytest.fixture
def color_refs(request):

    cian = Color.create("doc_id_cian")
    cian.name = 'cian'
    cian.save()

    magenta = Color.create("doc_id_magenta")
    magenta.name = "magenta"
    magenta.save()

    yellow = Color.create("doc_id_yellow")
    yellow.name = "yellow"
    yellow.save()

    black = Color.create("black")
    black.name = "black"
    black.save()

    def fin():
        cian.delete()
        magenta.delete()
        yellow.delete()
        black.delete()

    request.addfinalizer(fin)

    return [cian.doc_ref,
            magenta.doc_ref,
            yellow.doc_ref,
            black.doc_ref
            ]


@pytest.fixture
def setup_app(CTX):

    description = "A list of colors (may be filtered by palette)"

    app = Flask(__name__)
    swagger = Swagger(app)

    return app


class ColorSchema(schema.Schema):
    name = fields.Str()


class ColorDomainModelBase(domain_model.DomainModel):
    _collection_name = "colors"


Color = factory.ClsFactory.create(
    name="Color",
    schema=ColorSchema,
    base=ColorDomainModelBase
)


def test_rainbow_stuffs(CTX, setup_app, color_refs):
    app = setup_app

    assert isinstance(app, Flask)

    test_client = app.test_client()

    class RainbowSchema(schema.Schema):
        rainbow_name = fields.Raw(dump_only=True)
        colors = fields.Raw(dump_only=True)

    class RainbowViewModel(view.FlaskAsViewMixin, view_model.ViewModel):

        _schema_cls = RainbowSchema
        _color_d = dict()

        @property
        def colors(self):
            return list(self._color_d.values())

        @property
        def rainbow_name(self):
            return "-".join(self._color_d.values())

        def set_color(self, color_name):
            self._color_d[color_name] = color_name

        @classmethod
        def get_from_color_names(cls, color_names):
            struct = dict()

            for color_name in color_names:
                obj_type = "Color"
                doc_id = "doc_id_{}".format(color_name)

                def update_func(vm: RainbowViewModel, dm: Color):
                    vm.set_color(dm.name)

                struct[color_name] = (obj_type, doc_id, update_func)
            return super().get(struct_d=struct)

        @classmethod
        def new(cls, color_names: str=None):
            color_name_list = color_names.split("+")
            return cls.get_from_color_names(color_names=color_name_list)

    mediator = view_mediator.ViewMediator(
        view_model_cls=RainbowViewModel,
        app=app
    )
    mediator.add_instance_get(rule="/rainbow/<string:color_names>")

    res = test_client.get(
        path="/rainbow/yellow+magenta+cian")

    assert res.json == {
        'rainbowName': 'yellow-magenta-cian',
        'colors': ['yellow', 'magenta', 'cian']
    }
