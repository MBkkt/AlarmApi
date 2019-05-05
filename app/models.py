from sqlalchemy import or_, Column

from app import db
from app.errors import MyError
from werkzeug.security import generate_password_hash, check_password_hash

users_rooms = db.Table(
    'users_rooms',
    db.Column(
        'user_id', db.Integer, db.ForeignKey('user.id'),
    ),
    db.Column(
        'room_id', db.Integer, db.ForeignKey('room.id'),
    ),
)


class User(db.Model):
    """user - room : many-to-many
       user - msg  : one-to-many
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)
    rooms = db.relationship('Room', secondary=users_rooms,
                            backref=db.backref('users'), )

    @classmethod
    def register(cls, data):
        user = User.query.filter(or_(
            User.id == data.get('userId'),
            User.user_name == data.get('userName'),
            User.email == data.get('userEmail'))).first()
        if user:
            raise MyError("This user exist")
        if not all((data.get('userName'), data.get('userEmail'),
                    data.get('userPassword'))):
            raise MyError("Bad name, mail, password")
        user = User(
            user_name=data['userName'],
            email=data['userEmail'],
            password_hash=generate_password_hash(data['userPassword'])
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def login(cls, data):
        user = User.query.filter(or_(
            User.id == data.get('userId'),
            User.user_name == data.get('userName'),
            User.email == data.get('userEmail'))).first()
        if not user:
            raise MyError("This user no exist")
        elif check_password_hash(user.password_hash,
                                 data.get('userPassword', '')):
            return user
        else:
            raise MyError("Password error")

    def send_msg(self, data):
        room = Room.query.filter_by(id=data.get('roomId')).first()
        if not room:
            raise MyError("This room no exist")
        if data.get('roomId') in (msg.room_id for msg in self.msgs):
            raise MyError("This msg exist")
        msg = Msg(body=data.get('msg', ''))
        db.session.add(msg)
        self.msgs.append(msg)
        room.msgs.append(msg)
        db.session.commit()
        return msg

    def create_room(self, data):
        room = Room.query.filter_by(
            room_name=data.get('room', {}).get('name')).first()
        if room:
            raise MyError("This room exist")
        room = Room(room_name=data.get('room', {}).get('name'),
                    admin_id=self.id)
        self.rooms.append(room)
        db.session.add(room)
        db.session.commit()
        return room

    def get_rooms(self):
        return [
            {'id': room.id, 'name': room.room_name, 'adminId': room.admin_id}
            for room in self.rooms
        ]


class Room(db.Model):
    """room - user  : many-to-many
       room - msg   : one-to-many
       room - alarm : one-to-many
    """
    __tablename__ = 'room'
    id: Column = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_name = db.Column(db.String, unique=True)
    admin_id = db.Column(db.Integer)

    @classmethod
    def get_room(cls, data):
        room = Room.query.filter_by(id=data.get('roomId')).first()
        if not room:
            raise MyError("This room no exist")
        return room

    @classmethod
    def get_rooms(cls, data):
        if not data.get('roomName'):
            raise MyError('bad roomName')
        return [
            {'id': room.id, 'name': room.room_name, 'adminId': room.admin_id}
            for room in
            Room.query.filter(Room.user_name.like(f"{data['roomName']}%")).all()
        ]


class Msg(db.Model):
    """msg - user : many-to-one
       msg - room : many-to-one
    """
    __tablename__ = 'msg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='msgs')
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='msgs')

    @classmethod
    def get_msg(cls, data):
        msg = Msg.query.filter_by(id=data.get('msgId')).first()
        if not msg:
            raise MyError("This msg no exist")
        return msg


class Alarm(db.Model):
    """alarm - room : many-to-one
    """
    __tablename__ = 'alarm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alarm_name = db.Column(db.String)
    counter = db.Column(db.Integer)
    time = db.Column(db.Time)
    days = db.Column(db.String(7))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='alarms')

    @classmethod
    def get_alarm(cls, data):
        alarm = Alarm.query.filter_by(id=data.get('alarmId')).first()
        if not alarm:
            raise MyError("This alarm no exist")
        return alarm

    @classmethod
    def check_alarm(cls, data):
        alarm = Alarm.query.filter_by(id=data.get('alarmId')).first()
        return not bool(alarm)

    def decrease(self):
        ans = False
        self.counter -= 1
        if self.counter == 0:
            Alarm.delete(self)
            ans = True
        db.session.commit()
        return ans
