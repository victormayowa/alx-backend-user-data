#!/usr/bin/env python3
"""
session login with db
"""
from datetime import datetime
from uuid import uuid4

from models.user_session import UserSession
from .session_exp_auth import SessionExpAuth

UserSession.load_from_file()


class SessionDBAuth(SessionExpAuth):
    """session login with db"""
    def create_session(self, user_id: str = None) -> str:
        """ Create a session and store it in the database """
        if user_id is None:
            return None

        session_id = str(uuid4())
        new_session = UserSession(user_id=user_id, session_id=session_id)
        new_session.save()

        return new_session.session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """f Retrieve user ID from the database based on session ID """
        if session_id is None or not isinstance(session_id, str):
            return None

        sess = UserSession.search({'session_id': session_id})
        if len(sess) == 0:
            return None

        session_obj = sess[0]
        if self.session_duration <= 0:
            return session_obj.user_id

        created = session_obj.created_at.timestamp()
        if datetime.now().timestamp() > created + self.session_duration:
            return None

        return session_obj.user_id

    def destroy_session(self, request=None):
        """ Destroy session stored in the database """
        if request is None:
            return False

        sid = self.session_cookie(request)
        if sid is None:
            return False

        sess = UserSession.search({'session_id': sid})
        if len(sess) == 0:
            return False

        sess[0].remove()
        return True