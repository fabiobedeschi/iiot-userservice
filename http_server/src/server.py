from typing import Optional

from flask import Blueprint, jsonify, render_template, request
from flask_accept import accept, accept_fallback

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


@server.route('/')
@accept('text/html')
def root_page():
    return render_template('root.html')


@server.route('/users', methods=['GET'])
@accept_fallback
def find_all_users():
    result = db.find_all_users()
    return jsonify(result), 200 if result else 404


@find_all_users.support('text/html')
def find_all_users_html():
    result = db.find_all_users()
    return render_template('table_collection.html', title='Users', name='users', collection=result)


@server.route('/users/<string:uuid>', methods=['GET'])
def find_user(uuid):
    result = db.find_user(uuid)
    return jsonify(result), 200 if result else 404


@server.route('/users/<string:uuid>', methods=['PUT', 'PATCH'])
def update_user(uuid):
    result = None
    if data := request.json:
        result = db.update_user(
            uuid=uuid,
            delta=data.get('delta', 0)
        )
    return jsonify(result), 200 if result else 404


@server.route('/waste_bins', methods=['GET'])
@accept_fallback
def find_all_waste_bins():
    result = db.find_all_waste_bins()
    return jsonify(result), 200 if result else 404


@find_all_waste_bins.support('text/html')
def find_all_waste_bins_html():
    result = db.find_all_waste_bins()
    return render_template('table_collection.html', title='Waste bins', name='waste_bins', collection=result)


@server.route('/waste_bins/<string:uuid>', methods=['GET'])
def find_waste_bin(uuid):
    result = db.find_waste_bin(uuid)
    return jsonify(result), 200 if result else 404


@server.route('/waste_bins/<string:uuid>', methods=['PUT', 'PATCH'])
def update_waste_bin(uuid):
    result = None
    if data := request.json:
        result = db.update_waste_bin(
            uuid=uuid,
            fill_level=data.get('fill_level'),
        )
    return jsonify(result), 200 if result else 404


# TODO: remove this before delivery
@server.route('/users/<string:uuid>', methods=['POST'])
def create_user(uuid):
    result = None
    if find_user(uuid)[1] == 404:
        result = db.insert_user(uuid)
    return jsonify(result), 201 if result else 409


# TODO: remove this before delivery
@server.route('/users/<string:uuid>', methods=['DELETE'])
def remove_user(uuid):
    result = None
    if find_user(uuid)[1] == 200:
        result = db.delete_user(uuid)
    return jsonify(result), 200 if result else 404
