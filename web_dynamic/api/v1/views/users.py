#!/usr/bin/python3
"""
Module for managing user resources.
"""
from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User
from flasgger.utils import swag_from


@app_views.route('/users', methods=['GET'], strict_slashes=False)
@swag_from('documentation/user/get.yml', methods=['GET'])
def list_users():
    """
    Retrieve a list of all users.
    """
    users = [user.to_dict() for user in storage.all(User).values()]
    return jsonify(users)


@app_views.route('/users/<string:user_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/user/get_id.yml', methods=['GET'])
def get_user(user_id):
    """
    Retrieve a user by their unique ID.
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    return jsonify(user.to_dict())


@app_views.route('/users/<string:user_id>', methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/user/delete.yml', methods=['DELETE'])
def delete_user(user_id):
    """
    Remove a user identified by their unique ID.
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    user.delete()
    storage.save()
    return jsonify({})


@app_views.route('/users/', methods=['POST'], strict_slashes=False)
@swag_from('documentation/user/post.yml', methods=['POST'])
def create_user():
    """
    Create a new user.
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    data = request.get_json()
    if 'email' not in data:
        return make_response(jsonify({"error": "Missing email"}), 400)
    if 'password' not in data:
        return make_response(jsonify({"error": "Missing password"}), 400)
    user = User(**data)
    user.save()
    return jsonify(user.to_dict()), 201


@app_views.route('/users/<string:user_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/user/put.yml', methods=['PUT'])
def update_user(user_id):
    """
    Update user details by their unique ID.
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(user, key, value)
    storage.save()
    return jsonify(user.to_dict())
