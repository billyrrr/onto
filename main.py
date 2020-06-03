from flask_boiler.view.query_delta import OnTriggerMixin
from flask_boiler.context import Context

Context.load()

to_trigger = OnTriggerMixin()
