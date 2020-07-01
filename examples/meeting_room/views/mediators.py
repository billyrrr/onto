
# class ExampleMediator:
#
#     source = object()  # Maybe use descriptor
#     sink = object()
#
#     @source.on_create
#     def create_booking(self):
#         # Do something
#         obj = None
#         self.sink.emit(obj)
#
#     @source.on_delete
#     def remove_booking(self):
#         obj = None
#         self.sink.emit(obj)
#
#     @source.on_event(filter='cancel')
#     def on_cancel(self):
#         obj = None
#         self.sink.update(obj, 'status', 'cancelled')
