import pytest

from onto.helpers import make_variable


def test_hello():
    from onto.helpers import make_variable

    ct1 = make_variable('ct1', default='ct1default')
    ct2 = make_variable('ct2', default='ct2default')

    with ct1('ct1a'):
        assert ct1.get() == 'ct1a'
        with ct1('ct1b'):
            assert ct1.get() == 'ct1b'

    assert ct1.get() == 'ct1default'


@pytest.mark.asyncio
async def test_async():
    ct1 = make_variable('ct1', default='ct1default')
    ct2 = make_variable('ct2', default='ct2default')

    async def trial(x):
        if x >= 10:
            return
        with ct1(f'ct1a_{x}'):
            assert ct1.get() == f'ct1a_{x}'
            await trial(x+1)
            assert ct1.get() == f'ct1a_{x}'
            with ct1(f'ct1b_{x}'):
                assert ct1.get() == f'ct1b_{x}'
                with ct2(f'ct2a_{x}'):
                    assert ct2.get() == f'ct2a_{x}'

    import asyncio
    for _ in range(100):
        asyncio.create_task(trial(0))
        asyncio.create_task(trial(1))
        asyncio.create_task(trial(2))

    await asyncio.sleep(2)

    # asyncio.create_task(cvget("main"))
