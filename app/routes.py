from flask import jsonify, request, make_response, abort
from app import app


class MyError(Exception):
    pass


import app.utils_routes as utils


@app.errorhandler(400)
def not_found(error):
    return make_response(
        jsonify({'error': 'Bad request, sosi hui, hz pochemu'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found this url'}), 404)


type_request = {
    0: utils.register,
    1: utils.login,
    2: utils.create_room,
    3: utils.change_room,
    4: utils.get_user_rooms,
    5: utils.send_request_to_room,
    6: utils.turn_off_alarm,
    7: utils.search_rooms,
    8: utils.check_alarm,
    9: utils.is_request_in_room,
    10: utils.get_room,
}


@app.route('/alarm_api', methods=['POST'])
def alarm_api():
    try:
        client_request = request.get_json()
        if isinstance(client_request, dict):
            return jsonify(
                type_request[client_request['requestType']](client_request)
            )
    except MyError as e:
        return jsonify({
            'error': str(e)
        })
    except Exception as e:
        print(e)
    abort(400)


@app.route('/')
def about():
    return 'Api by MBkkt for Alarm by alamasm'
