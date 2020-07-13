#
#
#
# if __name__ == "__main__":
#
#     coordinator = Coordinator()
#     coordinator.start()
#
#     class MyListener(Listener):
#
#         _coordinator = coordinator
#
#         @classmethod
#         def start(cls):
#             while True:
#                 import time
#                 time.sleep(2)
#                 cls._coordinator._on_snapshot(dict(foo='bar'))
#
#     k = MyListener\
#     k.start()
#
#     raise ValueError
