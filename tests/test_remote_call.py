from typing import Type

import pytest


@pytest.mark.asyncio
async def test_remote_call():

    from onto.domain_model import DomainModel

    class A(DomainModel):

        @classmethod
        async def do_classmethod(cls) -> None:
            print('classmethod')

        async def do_method(self) -> None:
            print("method")


    A.method_proxy(doc_id='foo')

    from onto.invocation_context import invocation_context_var
    from onto.invocation_context import InvocationContextEnum
    with invocation_context_var(InvocationContextEnum.STATEFUL_FUNCTIONS_INTERNAL):
        assert await A.initializer_proxy(doc_id='foo').do_classmethod() is None
        assert await A.method_proxy(doc_id='foo').do_method() is None
