from api_code import model
# from flask import abort
from datetime import time

model.db.create_all()


def register(data: dict) -> dict:
    ans = {
        'responseType': 0,
        'userId': -1,
        'registred': False,
    }
    if not model.User.query.filter_by(name=data['userName']).count():
        user = model.User(name=data['userName'], password=data['userPassword'])
        model.db.session.add(user)
        model.db.session.commit()
        ans['userId'] = user.id
        ans['registred'] = True
    return ans


def login(data: dict) -> dict:
    ans = {
        'responseType': 1,
        'logged': False,
        'userId': -1,
    }
    user = (model.User.query.filter_by(name=data['userName']).first() or
            model.User.query.filter_by(id=data['userId']).first())
    if user and data['userPassword'] == user.password:
        ans['userId'] = user.id
        ans['logged'] = True
    return ans


def create_room(data: dict) -> dict:
    ans = {
        'responseType': 2,
        'roomId': -1,
        'roomCreated': False,
    }
    admin = model.User.query.filter_by(id=data['userId']).first()
    room = model.Room.query.filter_by(name=data['room']['name']).first()
    if admin and data['userPassword'] == admin.password and not room:
        room = model.Room(name=data['room']['name'], password=data['room']['password'], admin_id=admin.id)
        room.linking.append(admin)
        model.db.session.add(room)
        model.db.session.commit()
        ans['roomId'] = room.id
        ans['roomCreated'] = True
    return ans


def change_room(data: dict) -> dict:
    ans = {
        'responseType': 3,
        'roomChanged': False,
    }
    room = model.Room.query.filter_by(id=data['room']['id']).first()
    if room:
        admin = model.User.query.filter_by(id=room.admin_id).first()
        if data['userId'] == admin.id and data['userPassword'] == admin.password:
            room.name = data['room']['name']
            room.password = data['room']['password']
            room.admin_id = data['room']['adminId']

            room.linking.extend(
                model.User.query.filter(
                    model.User.id.in_(
                        [user['id'] for user in data['room']['users']]
                    )
                ).all()
            )

            temp = []
            for alarm in data['room']['alarms']:
                alarm = (
                        model.Alarm.query.filter_by(id=alarm['id']).first()
                        or
                        model.Alarm(
                            name=alarm['name'],
                            counter=0,
                            time=time(hour=alarm['time'][0], minute=alarm['time'][1], ),
                            days=''.join(map(str, alarm['days'])),
                        )
                )
                alarm.counter = room.linking.count()
                temp.append(alarm)
            room.alarms = temp

            model.db.session.commit()
            ans['roomChanged'] = True
    return ans


def get_rooms(data: dict) -> dict:
    ans = {
        'responseTyp': 4,
        'userId': -1,
        'rooms': [],
    }
    user = model.User.query.filter_by(id=data['userId']).first()
    if user and data['userPassword'] == user.password:
        ans['userId'] = user.id
        ans['rooms'] = [
            {'id': room.id, 'name': room.name, 'adminId': room.admin_id}
            for room in user.room
        ]
    return ans


def send_request_to_room(data: dict) -> dict:
    ans = {
        'responseType': 5,
        'msg': -1,
        'requestSent': False,
    }
    room = model.Room.query.filter_by(id=data['roomId']).first()
    user = model.User.query.filter_by(id=data['userId']).first()
    check_msg = model.Msg.query.filter_by(user_id=data['userId'], room_id=data['roomId']).first()
    if room and user and data['userPassword'] == user.password and not check_msg:
        msg = model.Msg(msg=data['msg'])
        model.db.session.add(msg)
        user.msgs.append(msg)
        room.msgs.append(msg)
        model.db.session.commit()
        ans['msg'] = msg.id
        ans['requestSent'] = True
    return ans


def turn_off_alarm(data: dict) -> dict:
    ans = {
        'responseType': 6,
        'turnedOff': False,
    }
    user = model.User.query.filter_by(id=data['userId']).first()
    alarm = model.Alarm.query.filter_by(id=data['alarmId']).first()
    if alarm and user and data['userPassword'] == user.password:
        alarm.counter -= 1
        ans['turnedOff'] = True
    return ans


def search_room(data: dict) -> dict:
    ans = {
        'responseType': 7,
        'rooms': [],
    }
    user = model.User.query.filter_by(id=data['userId']).first()
    if user and data['userPassword'] == user.password:
        ans['rooms'] = [
            {'id': room.id, 'name': room.name, 'adminId': room.admin_id, }
            for room in
            model.Room.query.filter(model.Room.name.in_([name for name in data['roomName']])).all()
        ]
    return ans


def check_alarm(data: dict) -> dict:
    user = model.User.query.filter_by(id=data['userId']).first()
    ans = {
        'responseType': 8,
        'allUsersTurnedOff': False,
        'alarmId': -1
    }
    if user and data['userPassword'] == user.password:
        alarm = model.Alarm.query.filter_by(id=data['alarmId']).first()
        if alarm:
            ans['alarmId'] = alarm.id
            if alarm.counter <= 0:
                model.db.session.delete(alarm)
                model.db.session.commit()
                ans['allUsersTurnedOff'] = True
    return ans


def is_request_in_room(data: dict) -> dict:
    ans = {
        'responseType': 9,
        'accepted': False,
        'roomId': -1,
    }
    user = model.User.query.filter_by(id=data['userId']).first()
    if user and data['userPassword'] == user.password:
        msg = model.Msg.query.filter_by(id=data['msgId']).first()
        if msg:
            room = model.Room.query.filter_by(id=msg.room_id).first()
            if room and user in room.linking:
                model.db.session.delete(msg)
                model.db.session.commit()
                ans['roomId'] = room.id
                ans['accepted'] = True
    return ans
