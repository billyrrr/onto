from flask_boiler.source import Protocol


def test_register():

    protocol = Protocol()

    @protocol._register('on_update')
    @protocol._register('on_create')
    def foo():
        print('foo invoked')

    assert protocol.mapping['on_create'] == 'foo'
    assert protocol.mapping['on_update'] == 'foo'

    assert False
