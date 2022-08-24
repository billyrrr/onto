"""
用于区分是否远程调用对象，以及调用的方式
"""
from contextvars import ContextVar
from enum import Enum, auto
from typing import Union, Callable

from onto.helpers import make_variable


class InvocationContextEnum(Enum):
    """
    用于区分远程调用的类型
    """

    # stateful functions 内部调用（推荐），这样可以实现 exactly-once 调用
    STATEFUL_FUNCTIONS_INTERNAL = auto()

    # 通过 kafka 发送至 stateful functions ingress，用于外部服务向服务内部调用
    KAFKA_TO_FUNCTIONS_INGRESS = auto()


invocation_context_var: Union[ContextVar[None], ContextVar['InvocationContextEnum'], Callable] = \
    make_variable('invocation_context', default=InvocationContextEnum.KAFKA_TO_FUNCTIONS_INGRESS)


from functools import wraps


# def remote_callable(f):
#
#     @wraps(f)
#     async def wrapper(*args, **kwds):
#         print('Calling decorated function')
#         return await f(*args, **kwds)
#     return wrapper
#
#
# def remote_method(f):
#
#     @wraps(f)
#     async def wrapper(_self, **kwds):
#         print('Calling decorated function')
#         return await f(*args, **kwds)
#     return wrapper
#



if __name__ == "__main__":
    pass
    # async def run():

