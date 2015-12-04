#########################################################################
## Define your tables below; for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

from datetime import datetime

db.define_table('board',
                Field('board_name', required=True))

db.define_table('post',
                Field('board', db.board),
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('post_name', required=True),
                Field('post_message', required=True),
                Field('post_id'),
                Field('post_time', 'datetime',))

db.post.id.readable = db.post.id.writable = False
db.post.board.readable = db.post.board.writable = False
db.post.board.ondelete = "SET NULL"
db.post.user_id.readable = db.post.user_id.writable = False
db.post.user_id.default = auth.user_id
db.post.post_time.readable = db.post.post_time.writable = False
db.post.post_time.default = datetime.utcnow()

db.define_table('player',
                Field('pos', required=True),
                Field('points', default=0),
                Field('yards', default=0),
                Field('touchdowns', default=0),
                Field('field_goals', default=0),
                Field('interceptions', default=0),
                Field('fumbles', default=0))

db.define_table('team',
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('name', required=True),
                Field('week_points', default=0),
                Field('total_points', default=0))