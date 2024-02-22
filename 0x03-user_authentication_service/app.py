#!/usr/bin/env python3
"""
Flask App
"""
from flask import Flask, jsonify, request, abort, redirect, url_for

from auth import Auth


app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET'])
def index():
    """Home Route"""
    return jsonify({'message': 'Bienvenue'})


@app.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    """
    Registers a new user
    """
    email = request.form.get('email')
    passwd = request.form.get('password')
    if not email or not passwd:
        return jsonify({'message': 'missing email or password'}), 400

    try:
        user = AUTH.register_user(email=email, password=passwd)
        payload = {'email': email, 'message': 'user created'}
        return jsonify(payload)
    except ValueError:
        return jsonify({'message': 'email already registered'}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    """logs a user in"""
    email = request.form.get('email')
    passwd = request.form.get('password')
    is_valid = AUTH.valid_login(email, passwd)
    if not is_valid:
        abort(401)

    session_id = AUTH.create_session(email)
    response = jsonify({'email': email, 'message': 'logged in'})
    response.set_cookie('session_id', session_id)

    return response


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    """Logs a user out"""
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    AUTH.destroy_session(user.id)
    return redirect('/')


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    """Returns user profile information."""
    session_id = request.cookies.get('session_id')
    if session_id is None:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    return jsonify({'email': user.email})


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    """Generates a password reset token."""
    email = request.form.get('email')
    if email is None:
        abort(400)

    try:
        token = AUTH.get_reset_password_token(email)
        return jsonify({'email': email, 'reset_token': token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    """
    updates user password
    """
    email = request.form.get('email')
    token = request.form.get('reset_token')
    passwd = request.form.get('new_password')

    if not email or not token or not passwd:
        abort(400)

    try:
        AUTH.update_password(token, passwd)
        return jsonify({'email': email, 'message': 'Password updated'})
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
