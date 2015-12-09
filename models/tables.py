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

db.define_table('team',
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('name', required=True),
                Field('ready', default=False),
                Field('week_points', default=0),
                Field('total_points', default=0))

db.team.user_id.readable = db.team.user_id.writable = False
db.team.ready.readable = db.team.ready.writable = False
db.team.week_points.readable = db.team.week_points.writable = False
db.team.total_points.readable = db.team.total_points.writable = False


db.define_table('player',
                Field('team', db.team, default=None),
                Field('name', required=True),
                Field('pos', requires=IS_IN_SET(['QB', 'RB', 'WR', 'TE', 'K'])),
                Field('points', default=0),
                Field('yards', default=0),
                Field('touchdowns', default=0),
                Field('field_goals', default=0),
                Field('interceptions', default=0),
                Field('fumbles', default=0))

db.player.id.readable = db.player.id.writable = False
db.player.team.readable = db.player.team.writable = False
db.player.points.readable = db.player.points.writable = False
db.player.yards.readable = db.player.yards.writable = False
db.player.touchdowns.readable = db.player.touchdowns.writable = False
db.player.field_goals.readable = db.player.field_goals.writable = False
db.player.interceptions.readable = db.player.interceptions.writable = False
db.player.fumbles.readable = db.player.fumbles.writable = False

db.define_table('draft',
                Field('turn'), default=0)

db.draft.turn.readable = db.draft.turn.writable = False