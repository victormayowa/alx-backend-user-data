#!/usr/bin/env python3
"""
session auth view
"""
from os import getenv

from api.v1.views import app_views
from flask import abort, jsonify, request

from models.user import User


@app_views.route('/auth_session/login', methods=['POST'],
                 strict_slashes=False)
def session_login():
    """ Handle user login """
    email = request.form.get('email', None)
    password = request.form.get('password', None)

    if email is None:
        return jsonify({"error": "email missing"}), 400
    if password is None:
        return jsonify({'error': 'password missing'}), 400

    user = User.search({'email': email})
    if len(user) == 0:
        return jsonify({'error': 'no user found for this email'}), 404
    if not user[0].is_valid_password(password):
        return jsonify({'error': 'wrong password'}), 401

    from api.v1.app import auth
    session_id = auth.create_session(user[0].id)
    session_name = getenv('SESSION_NAME', None)

    response = jsonify(user[0].to_json())
    response.set_cookie(session_name, session_id)

    return response


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def logout():
    """ Handle user logout """
    from api.v1.app import auth

    deleted = auth.destroy_session(request)
    if not deleted:
        abort(404)

    return jsonify({}), 200