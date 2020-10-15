from pony.orm import db_session, sql_debug

from onto.collection_mixin import db
from pony.orm.dbproviders.sqlite import SQLiteProvider



@db_session
def meeting():


    from examples.meeting_room.domain_models import Meeting
    m = Meeting.new(doc_id='ab', )
    m.status = "in-session"
    assert False

if __name__ == "__main__":
    from examples.meeting_room.domain_models import Meeting, Location, User, Ticket
    sql_debug(True)  # Output all SQL queries to stdout

    db.bind(SQLiteProvider, filename=':memory:', create_db=True)
    db.generate_mapping(check_tables=False, create_tables=True)
    meeting()
