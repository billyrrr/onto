from flask_boiler.view.query_delta import OnTriggerMixin
from flask_boiler.context import Context

Context.load()

to_trigger = OnTriggerMixin(resource="projects/flask-boiler-testing/databases/(default)/documents/gcfTest/{gcfTestDocId}")
