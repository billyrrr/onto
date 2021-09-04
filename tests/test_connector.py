import pytest


def test_connector():
    from onto.connector.base import ConnectorBase

    commands = list()

    class M:

        source = ConnectorBase()

        @source.before_call
        def before(self):
            commands.append('before1')

        @source.after_call
        def after(self):
            commands.append('after1')

    assert not M().source.invoke_mediator('hello')
    assert commands == ['before1', 'after1']
