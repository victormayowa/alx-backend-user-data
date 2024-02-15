#!/usr/bin/env python3
"""
the auth module
"""
import base64
import binascii
from typing import TypeVar

from models.user import User
from .auth import Auth


class BasicAuth(Auth):
    """Basic Auth"""

    def extract_base64_authorization_header(self, auth_header: str) -> str:
        """
        returns the authorization header
        """
        if auth_header is None or not isinstance(auth_header, str):
            return None
        if not auth_header.startswith('Basic '):
            return None

        return auth_header.lstrip('Basic ')

    def decode_base64_authorization_header(self, base64_header: str) -> str:
        """
        decodes and return encoded header
        """
        if base64_header is None or not isinstance(base64_header, str):
            return None

        try:
            return base64.b64decode(base64_header).decode('utf-8')
        except binascii.Error:
            return None

    def extract_user_credentials(self, auth_header: str) -> (str, str):
        """
        decoded credentials
        """
        if auth_header is None or not isinstance(auth_header, str):
            return None, None
        if ':' not in auth_header:
            return None, None

        delim_idx = auth_header.index(':')
        username = auth_header[:delim_idx]
        password = auth_header[delim_idx + 1:]

        return username, password

    def user_object_from_credentials(self, user_email: str,
                                     user_pwd: str) -> TypeVar('User'):
        """
        authenticatesuser
        """
        if not user_email or not isinstance(user_email, str):
            return None
        if not user_pwd or not isinstance(user_pwd, str):
            return None

        try:
            user = User.search({'email': user_email})
        except Exception:
            return None

        if len(user) == 0:
            return None
        if not user[0].is_valid_password(user_pwd):
            return None

        return user[0]

    def current_user(self, request=None) -> TypeVar('User'):
        """fetchescurrent user"""
        if not request:
            return None

        header = self.authorization_header(request)
        if header is None:
            return None

        header = self.extract_base64_authorization_header(header)
        if header is None:
            return None

        decoded_header = self.decode_base64_authorization_header(header)
        if decoded_header is None:
            return None

        email, passwd = self.extract_user_credentials(decoded_header)
        if not email:
            return None

        return self.user_object_from_credentials(email, passwd)
