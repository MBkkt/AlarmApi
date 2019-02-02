from api_code.flask_app import db

links = db.Table('links',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('room_id', db.Integer, db.ForeignKey('room.id')), )


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    room = db.relationship('Room', secondary=links, backref=db.backref('linking', lazy='dynamic'))


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    admin_id = db.Column(db.Integer)


class Msg(db.Model):
    __tablename__ = 'msg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='msgs')
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='msgs')


class Alarm(db.Model):
    __tablename__ = 'alarm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    counter = db.Column(db.Integer)
    name = db.Column(db.String)
    time = db.Column(db.Time)
    days = db.Column(db.String(7))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='alarms')
