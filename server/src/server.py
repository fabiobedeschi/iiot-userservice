from os import getenv
from typing import Optional

from flask import Blueprint, jsonify, request
from paho.mqtt import publish
from ujson import dumps

from .database import Database


def send_update(user, action, area):
    data = {'action': action, 'user': user}
    publish.single(
        topic=area,
        payload=dumps(data),
        hostname='mosquitto',
        port=1883,
        keepalive=1
    )


class UserServer:
    def __init__(self, db: Optional[Database] = None, send_updates: bool = True):
        self.db = db or Database()
        self.send_updates = send_updates

    def before_request(self):
        if not (self.db and self.db.connection):
            self.db = Database()

    def find_all_users(self, data=None):
        data = data or {}
        if area := data.get('area'):
            result = self.db.find_users_by_area(area)
        else:
            result = self.db.find_all_users()
        return result, 200

    def find_user(self, uuid):
        result = self.db.find_user(uuid)
        return result, 200 if result else 404

    def update_user(self, uuid, data=None):
        data = data or {}
        delta = data.get('delta')
        area = data.get('area')

        result = self.db.update_user(uuid=uuid, delta=delta, area=area)
        if result:
            if self.send_updates:
                old_area = result.get('old_area')
                if old_area:
                    send_update(user=result, action='delete', area=old_area)
                    send_update(user=result, action='create', area=area)
                else:
                    send_update(user=result, action='update', area=area)
            return result, 200
        else:
            return None, 404

    def create_user(self, uuid, data=None):
        data = data or {}
        area = data.get('area')
        delta = data.get('delta')
        if not self.db.find_user(uuid):
            result = self.db.insert_user(uuid=uuid, delta=delta, area=area)
            if self.send_updates:
                send_update(user=result, action='create', area=area)
            return result, 201
        else:
            return None, 409

    def remove_user(self, uuid):
        if self.db.find_user(uuid):
            result = self.db.delete_user(uuid=uuid)
            if self.send_updates:
                send_update(user=result, action='delete', area=result.get('area'))
            return result, 200
        else:
            return None, 404


# Flask blueprint initialization
server_blueprint = Blueprint('server', __name__)

# Global variables
server: Optional[UserServer] = None


@server_blueprint.before_request
def before_request():
    global server
    if not server:
        send_updates = True
        if 'true' == getenv('DISABLE_UPDATES', 'false'):
            send_updates = False
        server = UserServer(send_updates=send_updates)
    server.before_request()


@server_blueprint.route('/users', methods=['GET'])
def find_all_users():
    result, code = server.find_all_users(data=request.args)
    return jsonify(result), code


@server_blueprint.route('/users/<string:uuid>', methods=['GET'])
def find_user(uuid):
    result, code = server.find_user(uuid)
    return jsonify(result), code


@server_blueprint.route('/users/<string:uuid>', methods=['PUT', 'PATCH'])
def update_user(uuid):
    result, code = server.update_user(uuid, request.json)
    return jsonify(result), code


@server_blueprint.route('/users/<string:uuid>', methods=['POST'])
def create_user(uuid):
    result, code = server.create_user(uuid, request.json)
    return jsonify(result), code


@server_blueprint.route('/users/<string:uuid>', methods=['DELETE'])
def remove_user(uuid):
    result, code = server.remove_user(uuid)
    return jsonify(result), code
