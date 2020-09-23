from onto.source.protocol import Protocol
from unittest.mock import patch, call, ANY
from .fixtures import CTX

from examples.meeting_room.tests.fixtures import *


def test_register():

    protocol = Protocol()

    @protocol._register('on_update')
    @protocol._register('on_create')
    def foo():
        print('foo invoked')

    assert protocol.mapping['on_create'] == 'foo'
    assert protocol.mapping['on_update'] == 'foo'


def test_source(meeting, CTX):
    from onto.source.leancloud import BeforeSaveDomainModelSource as dms

    with patch.object(dms, '_invoke_mediator') as mock_method:
        import leancloud
        cla = leancloud.Object.extend('Meeting')
        cla_obj = cla(
            **meeting.to_dict()
        )

        from examples.meeting_room.domain_models import Meeting
        source = dms(Meeting)
        source._call(
            cla_obj
        )
        assert mock_method.call_args_list == [call(func_name='before_save', obj=ANY)]
