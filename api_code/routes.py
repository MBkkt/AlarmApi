from flask import jsonify, request, make_response

from api_code import app
from api_code import response_func as func


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request, sosi hui, hz pochemu'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found this url'}), 404)


type_request = {
    # Пиши комменты, что не работает\работает не так что добавить и тд сюда
    0: func.register,
    # check
    1: func.login,
    # check
    2: func.create_room,
    # check
    3: func.change_room,
    # check
    4: func.get_rooms,
    # check
    5: func.send_request_to_room,
    # check
    6: func.turn_off_alarm,
    # check
    7: func.search_room,
    # check
    8: func.check_alarm,
    # check
    9: func.is_request_in_room,
    # check
}


@app.route('/alarm_api', methods=['GET', 'POST'])
def alarm_api():
    client_request: dict = request.json
    return jsonify(type_request[client_request['requestType']](client_request))
