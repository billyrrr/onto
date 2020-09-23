from examples.meeting_room.domain_models import Meeting
from examples.meeting_room.view_models import MeetingSession
from onto.query.query import ViewModelQuery
from onto.view import Mediator


class MeetingSessionPatch(Mediator):
    from onto import source, sink

    source = source.firestore(
        query=ViewModelQuery.patch_query(parent=MeetingSession)
    )
    sink = sink.firestore()

    @source.triggers.on_create
    def patch_meeting(self, ref, snapshot):
        """ TODO: add transaction

        :param ref:
        :param snapshot:
        :return:
        """
        d = snapshot.to_dict()
        meeting_id = d["target_meeting_id"]

        d = {
            Meeting.get_schema_cls().g(key): val
            for key, val in d.items() if key in {"inSession",}
        }

        user_id = ref.params[1]

        obj = MeetingSession.get(
            doc_id=meeting_id,
            once=True,
        )
        obj.update_vals(user_id=user_id, with_dict=d)
        # TODO: switch to notify
        obj.propagate_change()


class MeetingSessionGet(Mediator):

    from onto import source, sink

    source = source.domain_model(Meeting)
    sink = sink.firestore()  # TODO: check variable resolution order

    @source.triggers.on_update
    @source.triggers.on_create
    def materialize_meeting_session(self, obj):
        meeting = obj
        assert isinstance(meeting, Meeting)

        def notify(obj):
            for ref in obj._view_refs:
                self.sink.emit(reference=ref, snapshot=obj.to_snapshot())

        _ = MeetingSession.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )
        # mediator.notify(obj=obj)

    @classmethod
    def start(cls):
        cls.source.start()


class MeetingSessionLc(MeetingSession):

    @classmethod
    def _datastore(cls):
        from onto.context import Context as CTX
        return CTX.dbs.leancloud


class MeetingSessionShow(Mediator):

    from onto import source
    from onto.sink.leancloud import LcSink

    source = source.domain_model(Meeting)
    sink = LcSink()  # TODO: check variable resolution order

    @source.triggers.on_update
    @source.triggers.on_create
    def materialize_meeting_session(self, obj):
        meeting = obj
        assert isinstance(meeting, Meeting)

        def notify(obj):
            for ref in obj._view_refs:
                self.sink.emit(ref=ref, snapshot=obj.to_snapshot())

        _ = MeetingSessionLc.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )
        # mediator.notify(obj=obj)

    @classmethod
    def start(cls):
        cls.source.start()
