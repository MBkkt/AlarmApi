from datetime import time

from api_code.model import db, User, Room, Msg, Alarm

db.create_all()


def _checker(user_db, user_request, true_agrs=(), false_args=()):
    return all((
        user_db,
        user_db.id == user_request.get('userId') or user_db.name == user_request.get('userName'),
        user_db.password == user_request.get('userPassword'),
        all(true_agrs),
        not any(false_args),
    ))


def register(data: dict) -> dict:
    ans = {
        'responseType': 0,
        'registred': False,
        'userId': -1,
    }
    user = User.query.filter_by(name=data['userName']).first()
    if not user:
        user = User(name=data['userName'], password=data['userPassword'])
        db.session.add(user)
        db.session.commit()
        ans['userId'] = user.id
        ans['registred'] = True
    else:
        ans['error'] = -2  # 'this name exist'
    return ans


def login(data: dict) -> dict:
    ans = {
        'responseType': 1,
        'logged': False,
        'userId': -1,
        'error': 1
    }
    user = User.query.filter_by(id=data['userId']).first() or User.query.filter_by(name=data['userName']).first()
    if _checker(user, data):
        ans['userId'] = user.id
        ans['logged'] = True
    elif not user:
        ans['error'] = -2  # 'no exist this id and login'
    else:
        ans['error'] = -3  # 'bad password;
    return ans


def create_room(data: dict) -> dict:
    ans = {
        'responseType': 2,
        'roomCreated': False,
        'roomId': -1,
    }
    admin = User.query.filter_by(id=data['userId']).first()
    room = Room.query.filter_by(name=data['room']['name']).first()
    if _checker(admin, data, false_args=(room,)):
        room = Room(name=data['room']['name'], admin_id=admin.id)
        room.linking.append(admin)
        db.session.add(room)
        db.session.commit()
        ans['roomId'] = room.id
        ans['roomCreated'] = True
    return ans


def change_room(data: dict) -> dict:
    ans = {
        'responseType': 3,
        'roomChanged': False,
    }
    room = Room.query.filter_by(id=data['room']['id']).first()
    admin = User.query.filter_by(id=room.admin_id).first()
    if _checker(admin, data):
        room.name = data['room']['name']
        room.admin_id = data['room']['adminId']
        room.linking.extend(
            User.query.filter(
                User.id.in_(
                    [user['id'] for user in data['room']['users']]
                )
            ).all()
        )
        temp = []
        for alarm in data['room']['alarms']:
            alarm = Alarm.query.filter_by(id=alarm['id']).first() or Alarm(
                name=alarm['name'],
                counter=0,
                time=time(hour=alarm['time'][0], minute=alarm['time'][1], ),
                days=''.join(map(str, alarm['days'])),
            )
            alarm.counter = room.linking.count()
            temp.append(alarm)
        room.alarms = temp
        db.session.commit()
        ans['roomChanged'] = True
    return ans


def get_rooms(data: dict) -> dict:
    ans = {
        'responseType': 4,
        'userId': -1,
        'rooms': [],
    }
    user = User.query.filter_by(id=data['userId']).first()
    if _checker(user, data):
        ans['userId'] = user.id
        ans['rooms'] = [
            {'id': room.id, 'name': room.name, 'adminId': room.admin_id}
            for room in user.room
        ]
    return ans


def send_request_to_room(data: dict) -> dict:
    ans = {
        'responseType': 5,
        'requestSent': False,
        'msg': -1,
    }
    room = Room.query.filter_by(id=data['roomId']).first()
    user = User.query.filter_by(id=data['userId']).first()
    msg = Msg.query.filter_by(user_id=data['userId'], room_id=data['roomId']).first()
    if _checker(user, data, (room,), (msg,)):
        msg = Msg(msg=data['msg'])
        db.session.add(msg)
        user.msgs.append(msg)
        room.msgs.append(msg)
        db.session.commit()
        ans['msg'] = msg.id
        ans['requestSent'] = True
    return ans


def turn_off_alarm(data: dict) -> dict:
    ans = {
        'responseType': 6,
        'turnedOff': False,
    }
    user = User.query.filter_by(id=data['userId']).first()
    alarm = Alarm.query.filter_by(id=data['alarmId']).first()
    if _checker(user, data, (alarm,)):
        alarm.counter -= 1
        ans['turnedOff'] = True
    return ans


def search_room(data: dict) -> dict:
    ans = {
        'responseType': 7,
        'rooms': [],
    }
    user = User.query.filter_by(id=data['userId']).first()
    if _checker(user, data):
        ans['rooms'] = Room.query.filter_by(id=data.get('roomId'))
        ans['rooms'] = [
            {'id': room.id, 'name': room.name, 'adminId': room.admin_id}
            for room in ans['rooms'].all() or
                        Room.query.filter(Room.name.like(f"{data['roomName']}%")).all()
        ]
    return ans


def check_alarm(data: dict) -> dict:
    ans = {
        'responseType': 8,
        'allUsersTurnedOff': False,
        'alarmId': -1,
    }
    user = User.query.filter_by(id=data['userId']).first()
    alarm = Alarm.query.filter_by(id=data['alarmId']).first()
    if _checker(user, data, (alarm,)) and alarm.counter <= 0:
        db.session.delete(alarm)
        db.session.commit()
        ans['alarmId'] = alarm.id
        ans['allUsersTurnedOff'] = True
    return ans


def is_request_in_room(data: dict) -> dict:
    ans = {
        'responseType': 9,
        'accepted': False,
        'roomId': -1,
    }
    user = User.query.filter_by(id=data['userId']).first()
    msg = Msg.query.filter_by(id=data['msgId']).first()
    room = Room.query.filter_by(id=msg.room_id).first()
    if _checker(user, data, (room,)) and user in room.linking:
        db.session.delete(msg)
        db.session.commit()
        ans['roomId'] = room.id
        ans['accepted'] = True
    return ans
