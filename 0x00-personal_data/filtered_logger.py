#!/usr/bin/env python3
"""
FILTER and OBFUSCATE
"""
import os
import re
import logging
from typing import List
from mysql.connector.connection import MySQLConnection
from mysql import connector


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    REGEX FOR  IDENTIFICATION and
    REDACTING FIELDS FROM MESSAGE
    """
    for f in fields:
        reg = f'(?<={f}=)([^{separator}]+)(?={separator})'
        msg = re.sub(reg, redaction, message)

    return msg


def get_logger() -> logging.Logger:
    """
    CREATE AND RETURN LOGGER
    """
    log = logging.getLogger('user_data')
    log.setLevel(logging.INFO)
    log.propagate = False

    handle_stream = logging.StreamHandler()
    handle_stream.setFormatter(RedactingFormatter(PII_FIELDS))

    log.addHandler(handle_stream)

    return log


def get_db() -> MySQLConnection:
    """
    CREATE AND RETURN CONNECTED OBJECT
    """
    us = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    db = connector.connect(user=us, password=password,
                           host=host, database=db_name)

    return db


class RedactingFormatter(logging.Formatter):
    """
    REDACTS FORMAT
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """INITIALIZE"""
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        REDACT THE RECORD 
        MESSAGE AND FORMATS IT
        """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.msg, self.SEPARATOR)
        msg = super().format(record)
        return msg


def main():
    """
    CREATES A LOGGER
    """
    log = get_logger()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users;")
    for user in cursor:
        msg = (
            f"name={user[0]}; email={user[1]}; phone={user[2]}; "
            f"ssn={user[3]}; password={user[4]}; ip={user[5]}; "
            f"last_login={user[6]}; user_agent={user[7]};"
        )

        log.info(msg)


if __name__ == "__main__":
    main()