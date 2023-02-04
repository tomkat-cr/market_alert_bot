from pydantic import BaseModel
from bson.json_util import ObjectId

from .utility_general import get_default_db_resultset, \
    get_standard_base_exception_msg, log_debug
from .utility_db import db, verify_required_fields


class Session(BaseModel):
    _id: dict
    username: str
    token: str


# Low level methods


def fetch_session_by_entryname(entry_name, entry_value):
    resultset = get_default_db_resultset()
    log_debug(f'** DB ** fetch_user_by_entryname: {entry_name} {entry_value}')
    resultset['found'] = False
    try:
        resultset['resultset'] = db.sessions.find_one(
            {entry_name: entry_value}
        )
        resultset['found'] = resultset['resultset'] is not None
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(
            err, 'FSBEN1'
        )
        resultset['error'] = True
    return resultset


def create_session(json):
    mandatory_elements = {
        'username',
        'token',
    }
    resultset = verify_required_fields(
        json, mandatory_elements
    )
    if resultset['error']:
        return resultset

    db_row = fetch_session_by_entryname('username', json['username'])
    if db_row['resultset']:
        resultset['error_message'] = \
            f"Session for user {json['username']} already exists [CS4]."
    elif db_row['error']:
        resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    # json['creation_date'] = \
    #   json['update_date'] = current_datetime_timestamp()

    try:
        resultset['resultset']['_id'] = str(
            db.sessions.insert_one(json).inserted_id
        )
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(
            err, 'CS5'
        )
        resultset['error'] = True
    else:
        resultset['resultset']['rows_affected'] = '1'

    return resultset


def update_session(record):
    mandatory_elements = {
        'username',
        'token',
    }
    resultset = verify_required_fields(
        record, mandatory_elements, 'US1'
    )
    if resultset['error']:
        return resultset

    updated_record = dict(record)
    # updated_record['update_date'] = current_datetime_timestamp()

    if '_id' in updated_record:
        # To avoid "WriteError('Performing an update on the path '_id'
        # would modify the immutable field '_id')
        del updated_record['_id']

    log_debug(f'$$$ update_session.record: {record}')
    log_debug(f'$$$ update_session.updated_record: {updated_record}')

    try:
        resultset['resultset']['rows_affected'] = str(
            db.sessions.update_one(
                {'_id': ObjectId(record['_id'])},
                {'$set': updated_record}
            ).modified_count
        )
    except BaseException as err:
        resultset['error_message'] = \
            get_standard_base_exception_msg(err, 'US2')
        resultset['error'] = True

    return resultset


# High level method


def get_session(username: str):
    resultset = fetch_session_by_entryname('username', username)
    if not resultset['error'] and resultset['found']:
        resultset['data'] = Session(**resultset['resultset'])
    return resultset
