# from datetime import timedelta
from typing import Union

from pydantic import BaseModel

from .utility_general import get_default_db_resultset, \
    get_standard_base_exception_msg, log_debug
from .utility_db import db


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


# Low level methods


def fetch_user_by_entryname(entry_name, entry_value):
    resultset = get_default_db_resultset()
    log_debug(f'** DB ** fetch_user_by_entryname: {entry_name} {entry_value}')
    resultset['found'] = False
    try:
        resultset['resultset'] = db.users.find_one({entry_name: entry_value})
        resultset['found'] = resultset['resultset'] is not None
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(
            err, 'FUBEN1'
        )
        resultset['error'] = True
    return resultset


# High level method


def get_user(username: str):
    resultset = fetch_user_by_entryname('username', username)
    if not resultset['error'] and resultset['found']:
        resultset['data'] = User(**resultset['resultset'])
    return resultset
