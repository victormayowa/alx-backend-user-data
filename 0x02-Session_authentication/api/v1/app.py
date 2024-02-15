#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from typing import Tuple
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

auth = getenv('AUTH_TYPE', None)
if auth == 'basic_auth':
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
elif auth == 'session_auth':
    from api.v1.auth.session_auth import SessionAuth
    auth = SessionAuth()
elif auth == 'session_exp_auth':
    from api.v1.auth.session_exp_auth import SessionExpAuth
    auth = SessionExpAuth()
elif auth == 'session_db_auth':
    from api.v1.auth.session_db_auth import SessionDBAuth
    auth = SessionDBAuth()
else:
    from api.v1.auth.auth import Auth
    auth = Auth()

@app.before_request
def before_request():
    """
    authorize before passing to the
    request handler
    """
    if auth is None:
        return
    excluded_paths = ['/api/v1/status/', '/api/v1/unauthorized/',
                      '/api/v1/forbidden/', '/api/v1/auth_session/login/']
    if not auth.require_auth(request.path, excluded_paths):
        return

    auth_header = auth.authorization_header(request)
    session_cookie = auth.session_cookie(request)
    if not auth_header and not session_cookie:
        abort(401)

    request.current_user = auth.current_user(request)
    if not request.current_user:
        abort(403)


@app.errorhandler(404)
def not_found(error) -> Tuple[str, int]:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> Tuple[str, int]:
    """errorhandler for unauthorization error"""
    err = jsonify({"error": "Unauthorized"}), 401
    return err


@app.errorhandler(403)
def forbidden(error) -> Tuple[str, int]:
    """errorhandler for unauthorization error"""
    err = jsonify({"error": "Forbidden"}), 403
    return err


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)