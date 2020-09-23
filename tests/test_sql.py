# def test_table():
#     from sqlalchemy import MetaData, Table, Column, Integer, String, \
#         create_engine, select
#
#     metadata = MetaData()
#
#     user = Table('user', metadata,
#                  Column('user_id', Integer, primary_key=True),
#                  Column('user_name', String(16), nullable=False),
#                  Column('email_address', String(60)),
#                  Column('nickname', String(50), nullable=False)
#     )
#     user.named_with_column = True
#
#     engine = create_engine('sqlite:///:memory:')
#     metadata.create_all(engine)
#
#     with engine.connect() as con:
#
#         k = user.insert().values({
#             'user_id': 1,
#             'user_name': 'Bill',
#             'email_address': 'ss@sss.com',
#             'nickname': 'billy'
#         })
#
#         con.execute(k)
#
#         i = user.select()
#         i = con.execute(i)
#         for row in i:
#             # assert row == (1, 'Bill', 'ss@sss.com', 'billy')
#             print(dict(row))
#             # from sqlalchemy.ext.serializer import loads
#             # res = loads(row., metadata=metadata, scoped_session=con, engine=engine)
#             # print(res)
#
#
# # def test_create_table():
# #
# #     from pyflink.dataset import ExecutionEnvironment
# #     from pyflink.table import TableConfig, DataTypes, StreamTableEnvironment
# #     from pyflink.table.descriptors import
# #
# #     exec_env = ExecutionEnvironment.get_execution_environment()
# #     exec_env.set_parallelism(1)
# #     t_config = TableConfig()
# #     t_env = StreamTableEnvironment.create(exec_env, t_config)
# #     t_env.connect(.)
# #     t_env.execute_sql(
# #         "CREATE TABLE Orders (`user` BIGINT, product STRING, amount INT) WITH (...)")
# #
#
#
# def test_couchdb():
#     from onto.context import Context
#
#     # import couchdb
#     # couch: couchdb.Server = Context.dbs.couch
#     # couch.create('mydb')
#     # db = couch['mydb']
#     # doc = {'hello': 'world'}
#     # db.save(doc)
#
#     from onto.database.couch import CouchDatabase, Reference, Snapshot
#     db = CouchDatabase()
#     ref = Reference().child('users').child('userid1').child('bookings').child('bookingid1')
#     snapshot = Snapshot(hello='world')
#     db.set(
#         ref=ref,
#         snapshot=snapshot
#     )
#
#
# def test_couchbase():
#     from onto.context import Context
#
#     # import couchdb
#     # couch: couchdb.Server = Context.dbs.couch
#     # couch.create('mydb')
#     # db = couch['mydb']
#     # doc = {'hello': 'world'}
#     # db.save(doc)
#
#     from onto.database.couchbase import CouchbaseDatabase, Reference, Snapshot
#     db = CouchbaseDatabase()
#     ref = Reference().child('users').child('userid1').child('bookings').child('bookingid1')
#     snapshot = Snapshot(hello='world')
#     db.set(
#         ref=ref,
#         snapshot=snapshot
#     )
