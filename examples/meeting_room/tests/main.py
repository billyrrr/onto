from pony.orm import db_session, sql_debug, select, count
from pony.orm.core import Entity, left_join
from examples.meeting_room.domain_models.location import Location

from onto import attrs
from onto.collection_mixin import db
from pony.orm.dbproviders.sqlite import SQLiteProvider


def f(p):
    return 'P'


def g(q):
    return 'Q'


from pony.orm import raw_sql


class InsertMixin:

    @classmethod
    def _insert_dynamic_table(entity):


        def f(x, y):
            return x, y
            # avdict = {}
            # for attr in entity._attrs_:
            #     # import functools
            #     monad = getattr(entity, attr.name).(x, y)
            #     # p = functools.partial(monad, owner=entity)
            #     # res = select(getattr(m, attr.name) for m in Meeting)
            #     avdict[attr] = monad(x)
            # if entity._pk_is_composite_:
            #     from pony.py23compat import imap
            #     pkval = tuple(imap(avdict.get, entity._pk_attrs_))
            #     if None in pkval: pkval = None
            # else:
            #     pkval = avdict.get(entity._pk_attrs_[0])
            #
            # d = dict()
            # for attr in avdict:
            #     # TODO: support columns
            #     val = avdict[attr]
            #     if val is None: continue
            #     d[attr.name] = val
            #
            # table_name = entity._table_  # TODO: may need to do db.get_table(entity._table_)


        def op(x, y):
            return (x.status, y)

        def g():
            return (
                (x,y)
                for x in MeetingTwo
                for y in x.tickets
            )

        def query_gen(f, g):
            return select( f(x, y) for x,y in g() )

        def fg(m):
            return m.location.latitude

        def lng(m):
            return m.location.longitude

        im = query_gen(f=op, g=g)

        from pony.orm.sqltranslation import SqlQuery
        ast = im._translator.construct_subquery_ast(aliases=['store.status', 'store.ticket'])
        sql, adapter = db._ast2sql(ast)

        # from pony.py23compat import values_list
        #
        # arguments = adapter(values_list(kw))
        # return sql
        return sql


from examples.meeting_room.domain_models import Meeting

class MeetingTwo(Meeting, InsertMixin):

    ct = attrs.integer(type_cls=int)
    # latlng = attrs.string(type_cls=str)

    @property
    def latlng(self):
        return str(self.location.latitude) + str(self.location.longitude)

    @Meeting.status.getter
    def status(self):
        return 's'

    @ct.getter
    def ct(self):
        return sum(count(1) for t in Ticket if t.attendance)



# class MeetingSession:
#
#     @row_iter
#     def meetings(cls):
#         """ yields the source of each row
#
#         :return:
#         """
#         for m in Meeting:
#             for t in Ticket:
#                 yield Store(
#                     meeting=m,
#                     ticket=t,
#                 )


@db_session
def meeting():


    # m = Meeting.new(doc_id='ab', )
    # m.status = "in-session"

    res = MeetingTwo._insert_dynamic_table()
    print(res)
    assert None is not None



    meetings = lambda: (m for m in Meeting)

    def in_session_meetings(meetings):
        for m in meetings:
            if m.status == 'in-session':
                yield m

    def cti(meeting):
        return meeting.status == 'in-session'

    # def ct(meetings):
    #     for m in meetings:
    #         yield cti()

    s = select(cti(m) for m in meetings()).get_sql()
    print(s)

if __name__ == "__main__":
    from examples.meeting_room.domain_models import Meeting, Location, User, Ticket
    sql_debug(True)  # Output all SQL queries to stdout

    db.bind(SQLiteProvider, filename=':memory:', create_db=True)
    db.generate_mapping(check_tables=False, create_tables=True)
    meeting()

    assert False
