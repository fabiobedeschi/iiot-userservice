from typing import Optional

from flask import Blueprint, jsonify, request
from paho.mqtt import publish
from json import dumps

from .database import Database

# Flask blueprint initialization
server = Blueprint('server', __name__)

# Global variables
db: Optional[Database] = None


@server.before_request
def before_request():
    global db
    if not (db and db.connection):
        db = Database()


@server.route('/users', methods=['GET'])
def find_all_users():
    area = request.args.get('area', '')
    if area == '':
        result = db.find_all_users()
    else:
        result = db.find_users_by_area(area)
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['GET'])
def find_user(uuid):
    result = db.find_user(uuid)
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['PUT', 'PATCH'])
def update_user(uuid):
    result = None
    if data := request.json:
        delta = data.get('delta', -1000)
        area = data.get('area', '')
        result = db.update_user(
            uuid=uuid,
            delta=delta,
            area=area
        )
        old_area = result.get('old_area', '')
        if old_area != '':
            send_update(user={'uuid': uuid}, action='delete', area=result.get('old_area'))
            send_update(jsonify(result).get_json(), 'create', area)
        else:
            send_update(jsonify(result).get_json(), 'update', result.get('area'))
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['POST'])
def create_user(uuid):
    result = None
    if find_user(uuid)[1] == 404:
        if data := request.json:
            area = data.get('area', '')
            result = db.insert_user(uuid, area=area)
            send_update(jsonify(result).get_json(), 'create', area)
    return jsonify(result), 201 if result else 409


@server.route('/users/<string:uuid>', methods=['DELETE'])
def remove_user(uuid):
    result = None
    if find_user(uuid)[1] == 200:
        result = db.delete_user(uuid)
        send_update(user={'uuid': uuid}, action='delete', area=result.get('area'))
    return jsonify(result), 200 if result else 404


def send_update(user, action, area):
    data = {
        'action': action,
        'user': user
    }
    publish.single(topic=area, payload=dumps(data), hostname='mosquitto', port=1883, keepalive=1)
