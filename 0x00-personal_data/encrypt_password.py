#!/usr/bin/env python3
"""
HASH and ENCRYPTS
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """HASH PASSWORD"""
    s = bcrypt.gensalt()
    pwd = password.encode('utf-8')

    return bcrypt.hashpw(pwd, salt=s)


def is_valid(hashed_password: bytes, password: str) -> bool:
    """VERIFY PASSWORD"""
    pwd = password.encode('utf-8')
    valid_password = bcrypt.checkpw(pwd, hashed_password)

    return valid_password