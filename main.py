from onto.view.query_delta import OnTriggerMixin
from onto.context import Context

Context.load()

to_trigger = OnTriggerMixin(resource="projects/flask-boiler-testing/databases/(default)/documents/gcfTest/{gcfTestDocId}")
