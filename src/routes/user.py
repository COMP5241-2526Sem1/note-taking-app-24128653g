from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from src.models import user as user_model

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    col = user_model.get_user_collection()
    docs = col.find()
    return jsonify([user_model.to_public(d) for d in docs])


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    col = user_model.get_user_collection()
    doc = user_model.from_dict(data)
    res = col.insert_one(doc)
    created = col.find_one({'_id': res.inserted_id})
    return jsonify(user_model.to_public(created)), 201


@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        col = user_model.get_user_collection()
        doc = col.find_one({'_id': ObjectId(user_id)})
        if not doc:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(user_model.to_public(doc))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        col = user_model.get_user_collection()
        update = {}
        if 'username' in data:
            update['username'] = data['username']
        if 'email' in data:
            update['email'] = data['email']
        if update:
            col.update_one({'_id': ObjectId(user_id)}, {'$set': update})
        doc = col.find_one({'_id': ObjectId(user_id)})
        if not doc:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(user_model.to_public(doc))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@user_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        col = user_model.get_user_collection()
        res = col.delete_one({'_id': ObjectId(user_id)})
        if res.deleted_count == 0:
            return jsonify({'error': 'Not found'}), 404
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400
