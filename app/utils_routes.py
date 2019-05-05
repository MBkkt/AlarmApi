from datetime import time

from app.models import db, User, Room, Msg, Alarm

db.create_all()


def register(data: dict) -> dict:
    ans = {
        'registred': False,
        'userId': -1,
    }
    user: User = User.register(data)
    ans['userId'] = user.id
    ans['registred'] = True
    return ans


def login(data: dict) -> dict:
    ans = {
        'logged': False,
        'userId': -1,
    }
    user: User = User.login(data)
    ans['userId'] = user.id
    ans['logged'] = True
    return ans


def create_room(data: dict) -> dict:
    ans = {
        'roomCreated': False,
        'roomId': -1,
    }
    admin: User = User.login(data)
    room: Room = admin.create_room(data)
    ans['roomId'] = room.id
    ans['roomCreated'] = True
    return ans


def change_room(data: dict) -> dict:
    ans = {
        'roomChanged': False,
    }
    admin: User = User.login(data)
    room: Room = Room.get_room({'roomId': data.get('room', {}).get('id')})
    if admin.id == room.admin_id:
        room.name = data.get('room', {}).get('name') or room.room_name
        room.admin_id = data.get('room').get('adminId') or room.admin_id

        if data.get('room', {}).get('users') is not None:
            room.users = [
                user for user in
                User.query.filter(
                    User.id.in_([user['id'] for user in data['room']['users']])
                ).all()
            ]
        room.msgs = [
            msg for msg in room.msgs
            if msg.user not in room.users
        ]
        if data.get('room', {}).get('alarms') is not None:
            room.alarms.clear()
            for alarm in data['room']['alarms']:
                alarm = Alarm.query.filter_by(id=alarm['id']).first() or \
                        Alarm(
                            alarm_name=alarm['name'],
                            counter=0,
                            time=time(hour=alarm['time'][0],
                                      minute=alarm['time'][1], ),
                            days=''.join(map(str, alarm['days'])),
                        )
                alarm.counter = len(room.users)
                room.alarms.append(alarm)
        db.session.commit()
        ans['roomChanged'] = True
    return ans


def get_user_rooms(data: dict) -> dict:
    ans = {
        'rooms': [],
        'userId': -1,
    }
    user: User = User.login(data)
    ans['userId'] = user.id
    ans['rooms'] = user.get_rooms()
    return ans


def send_request_to_room(data: dict) -> dict:
    ans = {
        'msgSent': False,
        'msgId': -1,
    }
    user = User.login(data)
    msg = user.send_msg(data)
    ans['msgId'] = msg.id
    ans['msgSent'] = True
    return ans


def turn_off_alarm(data: dict) -> dict:
    ans = {
        'turnedOff': False,
        'deleted': False,

    }
    User.login(data)
    alarm: Alarm = Alarm.get_alarm(data)
    ans['deleted'] = alarm.decrease()
    ans['turnedOff'] = True
    return ans


def search_rooms(data: dict) -> dict:
    ans = {
        'rooms': [],
    }
    User.login(data)
    ans['rooms'] = Room.get_rooms(data)
    return ans


def check_alarm(data: dict) -> dict:
    ans = {
        'allUsersTurnedOff': False,
        'alarmId': -1,
    }
    User.login(data)
    ans['allUsersTurnedOff'] = Alarm.check_alarm(data)
    return ans


def is_request_in_room(data: dict) -> dict:
    ans = {
        'send': False,
        'roomId': -1,
    }
    user: User = User.login(data)
    room: Room = Room.get_room(data)
    if room.id in (msg.room_id for msg in user.msgs):
        ans['roomId'] = room.id
        ans['send'] = True
    return ans


def get_room(data: dict) -> dict:
    ans = {
        'room': {},
    }
    user: User = User.login(data)
    room: Room = Room.get_room(data)
    ans['room']['id'] = room.id
    ans['room']['name'] = room.room_name
    ans['room']['adminId'] = room.admin_id
    ans['room']['users'] = [
        {'id': user.id, 'name': user.user_name}
        for user in room.users
    ]
    ans['room']['unapprovedUsers'] = [
        {'id': msg.user_id} for msg in room.msgs
    ] if user.id == room.admin_id else []
    ans['room']['alarms'] = [
        {
            'id': alarm.id, 'name': alarm.alarm_name,
            'time': [alarm.time.hour, alarm.time.minute],
            'days': alarm.days, 'counter': alarm.counter,
        }
        for alarm in room.alarms
    ]
    return ans
