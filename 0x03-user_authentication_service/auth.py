#!/usr/bin/env python3
"""
Auth Module
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from bcrypt import hashpw, gensalt, checkpw

from db import DB
from user import User


def _hash_password(password: str) -> bytes:
    """
    Generate a salted hash of the input password
    """
    # Generate a salt
    salt = gensalt()
    # Hash the password with the salt
    hashed_password = hashpw(password.encode('utf-8'), salt)

    return hashed_password


def _generate_uuid() -> str:
    """Generates a new UUID."""
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database."""
    def __init__(self) -> None:
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user"""
        try:
            user = self._db.find_user_by(email=email)
            raise ValueError(f'User {email} already exists')
        except NoResultFound:
            pass

        passwd = _hash_password(password)

        return self._db.add_user(email, passwd)

    def valid_login(self, email: str, password: str) -> bool:
        """Validates user login."""
        try:
            user = self._db.find_user_by(email=email)
            return checkpw(password.encode('utf-8'), user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """
        generates new sessions
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return

    def get_user_from_session_id(self, session_id: str) -> Optional[User]:
        """Fetches a user from session_id."""
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Deletes a session"""
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user_id, session_id=None)
        except NoResultFound:
            return

    def get_reset_password_token(self, email: str) -> str:
        """
        creates a password reset token
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = str(uuid4())
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """
        updates a password given a
        reset token
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed = _hash_password(password)
            self._db.update_user(user.id, hashed_password=hashed,
                                 reset_token=None)
        except NoResultFound:
            raise ValueError
