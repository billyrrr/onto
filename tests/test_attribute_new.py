from typing import List, Optional, Dict

import typing

from onto import attrs
from onto.attrs.attribute_new import AttributeMixin, AttributeBase
from onto.domain_model import DomainModel


from onto.attrs import unit


def test_something():

    initial = unit.Monad(decor=unit.DecoratorBase.get_root())
    res = initial.of_type(type_cls=str).import_required

    fd = res.decor._marshmallow_field_constructor()
    from marshmallow import fields
    assert str(fd) == str(fields.String(required=True))

    def fget(self):
        return 'hello'

    _1 = res.getter(fget)

    assert _1.decor.fget == fget
    assert _1.decor.fget(self=None) == 'hello'


def test_in_class():

    initial = unit.Monad(decor=unit.DecoratorBase.get_root())

    class A:
        status = initial.of_type(type_cls=str)

        @status.getter
        def status(self):
            return 'ok'

    assert A.status.decor.fget(A()) == 'ok'


def test_list():

    initial = unit.Monad(decor=unit.DecoratorBase.get_root())

    class A:
        status_list = initial.list(
            value=initial.of_type(type_cls=str).import_required
        )

        @status_list.getter
        def status_list(self):
            return ['hello', 'world']

    assert A.status_list.decor.fget(A()) == ['hello', 'world']


def test_decorator():

    # _1 = unit.OfType(type_cls=str, decorated=None)
    # _2 = unit.ImportRequired(decorated=_1)
    #
    # from marshmallow import fields
    #
    # assert _2._marshmallow_field_cls == fields.String
    # assert _2._marshmallow_required
    # fd =_2._marshmallow_field_constructor()
    # assert str(fd) == str(fields.String(required=True))
    #
    # def fget(self):
    #     return 'hello'
    #
    # _3 = unit.Getter(fget=fget, decorated=_2)
    # assert _3.fget == fget

    attrs = AttributeBase.get_root()

    status = attrs.str.optional.data_key('status')

    # num_meetings = attrs.int.optional
    # meetings = attrs.list(value=attrs.str)

    from onto.mapper import fields
    from marshmallow.fields import missing_

    # assert str(fd) == str(fields.String(data_key='my_status', required=False))
    kwargs = status.decor._marshmallow_field_kwargs
    assert dict(kwargs) == {
        'data_key': 'status'
    }

    fd2 = status.marshmallow_field
    assert str(fd2) == str(fields.String(data_key='status', required=False, missing=str))

    monad3_1 = unit.MonadContext.context().data_key('my_status')
    with monad3_1:
        monad3_2_1 = unit.MonadContext.context().optional
        with monad3_2_1:
            fd3 = status._marshmallow_field_constructor()
            assert str(fd3) == str(fields.String(data_key='my_status', required=False, missing=str))
        monad3_2_2 = unit.MonadContext.context().data_key('the_status')
        with monad3_2_2:
            fd3 = status._marshmallow_field_constructor()
            assert str(fd3) == str(fields.String(data_key='the_status', required=False, missing=str))


def test_domain_model():

    attrs = AttributeBase.get_root()

    class Meeting(DomainModel):
        class Meta:
            collection_name = "meetings"
            case_conversion = False

        @classmethod
        def _datastore(cls):
            from onto.database import Database
            return Database()

        # location = attrs.relation.not_nested.dm_cls('Location')
            # (nested=False, dm_cls='Location')
        # users: Dict['Ticket', 'User'] = attrs.not_nested
        # users = users.dict(
        #     key=attrs.of_type('Ticket'),
        #     value=attrs.of_type('User').optional
        # )
        #     # (nested=False, dm_cls='User',
        #     #                    collection=list)
        # tickets: List['Ticket'] = attrs.relation.not_nested
        status: str = attrs

        num_meetings: int = attrs.int.optional.default_value(-1)  # TODO: remove default_value
        @num_meetings.getter
        def num_meetings(self):
            return len(self.meetings)

        meetings: typing.List[typing.AnyStr] = attrs.list(
            value=lambda at: at.str
        )

    # base1 = unit.DataKey(data_key='my_status', decorated=None)
    #
    # with decor_base(decor=base1):
    #     base2 = unit.ImportEnabled(base1)
    #     with decor_base(decor=base2):
    #         fd = Meeting.status._marshmallow_field_constructor()
    #
    from onto.mapper import fields

    # assert str(fd) == str(fields.String(data_key='my_status', required=False))
    context = unit.MonadContext.context().marshmallow_capable_base().string
    with context:
        fd2 = Meeting.status.marshmallow_field
    assert str(fd2) == str(fields.String(data_key='status', required=False))

    monad3_1 =context.data_key('my_status')
    with monad3_1:
        monad3_2_1 = unit.MonadContext.context().optional
        with monad3_2_1:
            fd3 = Meeting.status._marshmallow_field_constructor()
            assert str(fd3) == str(fields.String(data_key='my_status', required=False))
        monad3_2_2 = context.data_key('the_status')
        with monad3_2_2:
            fd3 = Meeting.status._marshmallow_field_constructor()
            assert str(fd3) == str(fields.String(data_key='the_status', required=False))

    # with decor_base(decor=base1):
    #     base2 = unit.ImportEnabled(base1)
    #     with decor_base(decor=base2):
    #         fd = Meeting.status._marshmallow_field_constructor()

    m = Meeting.new(status='ok', meetings=['meeting one', 'meeting_two'])
    assert m.status == 'ok'
    from testfixtures import compare, MappingComparison
    compare(m.to_dict(), MappingComparison({
        'status': 'ok',
        'num_meetings': 2,
        'meetings': ['meeting one', 'meeting_two']
    }, partial=True))

    from onto.models.utils import _graphql_object_type_from_attributed_class
    res = _graphql_object_type_from_attributed_class(Meeting, input=False)
    assert res


def test_graphql_custom_scalar_type():

    from onto.models.base import Serializable
    class MyString(Serializable):
        class Meta:
            unwrap = 'value'

        value: str = attrs.attrs.nothing

    class A1(DomainModel):
        message = attrs.attrs.embed(MyString)

    from onto.models.utils import _graphql_object_type_from_attributed_class
    res = _graphql_object_type_from_attributed_class(A1, input=False)
    assert str(res) == 'A1'
    assert A1.from_dict({'value': 'hello'}).message != 'hello'


# def test_monad():



#
# class Meeting(DomainModel):
#
#     class Meta:
#         collection_name = "meetings"
#
#     location = attrs.relation.not_nested.dm_cls('Location')
#         # (nested=False, dm_cls='Location')
#     users: Dict['Ticket', 'User'] = attrs.not_nested
#     users = users.dict(
#         key=attrs.of_type('Ticket'),
#         value=attrs.of_type('User').optional
#     )
#         # (nested=False, dm_cls='User',
#         #                    collection=list)
#     tickets: List['Ticket'] = attrs.relation.not_nested
#     status = attrs.string
#
#     with attrs.read_only:
#         num_meetings = attrs.integer.optional
#
#
# class Ticket(DomainModel):
#     role = attrs.string.required
#     user: Optional['User'] = attrs.relation.not_nested
#     attendance = attrs.bproperty(type_cls=bool)
#
#     meetings = attrs.relation(import_required=False, dm_cls='Meeting', collection=list, nested=False)
