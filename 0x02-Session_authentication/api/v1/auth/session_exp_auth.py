#!/usr/bin/env python3
"""
session login expiration
"""
from os import getenv
from datetime import datetime

from .session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """expiring session auth class"""
    def __init__(self) -> None:
        """ Initialize SessionExpAuth """
        self.session_duration = int(getenv('SESSION_DURATION') or 0)
        super().__init__()

    def create_session(self, user_id: str = None) -> str:
        """ Create a session with expiration """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None

        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now()
        }
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """ Return the user ID for a given session ID """
        if session_id is None:
            return None
        if not self.user_id_by_session_id.get(session_id, None):
            return None

        session_dict = self.user_id_by_session_id[session_id]
        if not session_dict.get('created_at', None):
            return None

        if self.session_duration <= 0:
            return session_dict.get('user_id', None)

        created = session_dict['created_at'].timestamp()
        if datetime.now().timestamp() > created + self.session_duration:
            return None

        return session_dict['user_id']