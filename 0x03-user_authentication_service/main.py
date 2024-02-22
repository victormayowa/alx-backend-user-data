#!/usr/bin/env python3
"""Integration Tests
"""
import requests


URL = 'http://localhost:5000'


def register_user(email: str, password: str) -> None:
    """
    tests the register user route
    """
    resp = requests.post(
        f'{URL}/users',
        data={'email': email, 'password': password},
    )
    assert resp.status_code == 200


def log_in_wrong_password(email: str, password: str) -> None:
    """
    tests log in with wrong password
    """
    resp = requests.post(
        f'{URL}/sessions',
        data={'email': email, 'password': password}
    )

    assert resp.status_code == 401


def log_in(email: str, password: str) -> str:
    """
    tests log in with wrong password
    """
    global sid
    resp = requests.post(
        f'{URL}/sessions',
        data={'email': email, 'password': password}
    )

    assert resp.status_code == 200
    assert resp.json() == {'email': email, 'message': 'logged in'}
    sid = resp.cookies.get('session_id')
    assert isinstance(sid, str)

    return sid


def profile_unlogged() -> None:
    """
    tests profile route without
    prior login
    """
    resp = requests.get(f'{URL}/profile')
    assert resp.status_code == 403


def profile_logged(session_id: str) -> None:
    """
    tests profile route without
    prior login
    """
    resp = requests.get(f'{URL}/profile', cookies={'session_id': session_id})

    assert resp.status_code == 200
    assert resp.json() == {'email': EMAIL}


def log_out(session_id: str) -> None:
    """tests log out endpoint"""
    resp = requests.delete(f'{URL}/sessions',
                           cookies={'session_id': session_id})
    resp = resp.history[0]
    assert resp.status_code == 302
    assert resp.is_redirect


def reset_password_token(email: str) -> str:
    """fetch reset token"""
    resp = requests.post(f'{URL}/reset_password', data={'email': email})
    assert resp.status_code == 200

    res_json = resp.json()
    reset_token = res_json.get('reset_token')

    assert res_json.get('email') == email
    assert 'reset_token' in res_json
    assert isinstance(reset_token, str)

    return reset_token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """updates password"""
    resp = requests.put(
        f'{URL}/reset_password',
        data={
            'email': email,
            'reset_token': reset_token,
            'new_password': new_password
        }
    )

    assert resp.status_code == 200
    assert resp.json() == {'email': email, 'message': 'Password updated'}


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
