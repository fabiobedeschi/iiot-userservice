from typing import Optional

from flask import Blueprint, jsonify, render_template, request
from flask_accept import accept, accept_fallback

from .database import Database

# Flask blueprint initialization
server = Blueprint('server', __name__)

# Global variables
db: Optional[Database] = None

# Mqtt Client
from paho.mqtt import publish


@server.before_request
def before_request():
    global db
    if not (db and db.connection):
        db = Database()


@server.route('/users', methods=['GET'])
def find_all_users():
    result = None
    area:str = request.args.get('area','')
    if area == '':
        result = db.find_all_users()
    else:
        result = db.find_user_by_area(area)
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['GET'])
def find_user(uuid):
    result = db.find_user(uuid)
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['PUT', 'PATCH'])
def update_user(uuid):
    result = None
    if data := request.json:
        delta: int = data.get('delta', -1000)
        area: str = data.get('area', "")
        result = db.update_user(
            uuid=uuid,
            delta=delta,
            area=area
        )
        old_area: str = result.get('old_area', "")
        if old_area != "":
            send_update(user={'uuid': uuid}, method='delete', area=result.get('old_area'))
            send_update(jsonify(result).get_json(), 'create', area)
        else:
            send_update(jsonify(result).get_json(), 'update', result.get('area'))
        print(jsonify(result).get_json())
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['POST'])
def create_user(uuid):
    result = None
    if find_user(uuid)[1] == 404:
        if data := request.json:
            area: str = data.get('area', "")
            result = db.insert_user(uuid, area=area)
            send_update(jsonify(result).get_json(), 'create', area)
    return jsonify(result), 201 if result else 409


@server.route('/users/<string:uuid>', methods=['DELETE'])
def remove_user(uuid):
    result = None
    if find_user(uuid)[1] == 200:
        result = db.delete_user(uuid)
        send_update(user={'uuid': uuid}, method='delete', area=result.get('area'))
    return jsonify(result), 200 if result else 404


def send_update(user, method, area):
    data = {
        "method": method,
        "user": user
    }
    publish.single(topic=area, payload=str(data), hostname="mosquitto", port=1883, keepalive=1)
