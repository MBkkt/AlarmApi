from flask import Flask, jsonify, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy

from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from api_code import response_func as func


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request, sosi hui, hz pochemu'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found this url'}), 404)


type_request = {
    0: func.register,
    1: func.login,
    2: func.create_room,
    3: func.change_room,
    4: func.get_user_rooms,
    5: func.send_request_to_room,
    6: func.turn_off_alarm,
    7: func.search_rooms,
    8: func.check_alarm,
    9: func.is_request_in_room,
    10: func.get_room,
}


@app.route('/alarm_api', methods=['POST'])
def alarm_api():
    try:
        client_request = request.get_json()
        if isinstance(client_request, dict):
            return jsonify(type_request[client_request['requestType']](client_request))
    except Exception as e:
        print(e)
    abort(400)


@app.route('/')
def about():
    return 'Api by MBkkt for Alarm by alamasm'
