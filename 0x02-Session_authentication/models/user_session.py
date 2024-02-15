#!/usr/bin/env python3
"""
model for user session
"""
from .base import Base


class UserSession(Base):
    """user session class"""
    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize UserSession """
        super().__init__(*args, **kwargs)
        self.user_id = kwargs.get('user_id', None)
        self.session_id = kwargs.get('session_id', None)