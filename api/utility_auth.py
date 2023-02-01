import json
from .settings import settings
from .utility_telegram import get_command_params, tg_delete_message, tg_send_message
from .utility_general import generic_api_call_raw, \
    get_api_standard_response, log_debug
from .model_sessions import get_session, create_session, update_session
from .utility_db import get_id_as_str


class auth_messages:
    AUTH_WITH_LOGIN_CMD = 'Please authenticate with the /login command'
    AUTH_SUCCEED = 'Authentication succeed'
    SESSION_NOT_UPDATED = 'Session couldn\'t be updated'
    USER_INACTIVE = 'User is not active. Please ask Tech Support for help'
    UNKNOWN_ERROR = 'Unknown error occurred'


def get_user_authentication(cmd_par):
    response = get_api_standard_response()
    username = cmd_par['user']['username']
    session_data = get_session(username)
    response['found'] = session_data['found']

    log_debug(f'** get_user_authentication.session_data: {session_data}')

    if session_data['error']:
        pass
    elif session_data['found']:
        # response['token'] = session_data['data'].token
        response['headers'] = dict({
            "Authorization": f"Bearer {session_data['resultset']['token']}"
        })
        response['userdata'] = None
    else:
        response['error'] = True
        response['error_message'] = \
            f'{auth_messages.AUTH_WITH_LOGIN_CMD}. [GUA-010]'
    return response


def login_handler(update, context):
    cmd_par = get_command_params(update, context)
    if cmd_par['error']:
        update.message.reply_text(cmd_par['error_message'])
        return
    post_data = dict()
    post_data['username'] = cmd_par['user']['username']
    if len(cmd_par['par']) > 0:
        post_data['password'] = cmd_par['par'][0]
    else:
        update.message.reply_text('ERROR: password not supplied')
        return

    tg_response = tg_delete_message(cmd_par['chat_id'], cmd_par['message_id'])
    log_debug(f'tg_delete_message.response={tg_response}')

    tg_response = tg_send_message(
        cmd_par['chat_id'], 
        f"/login {'*' * len(post_data['password'])}"
    )
    log_debug(f'tg_delete_message.response={tg_response}')

    url = settings.APIS_COMMON_SERVER_NAME + '/token'
    auth_data = generic_api_call_raw(url, 'Login Handler', body=post_data)
    log_debug(f'** login_handler.auth_data: {auth_data}')
    if auth_data['error']:
        if auth_data['response.status_code'] == 401:
            update.message.reply_text(
                json.loads(auth_data['response.text'])['detail']
            )
        else:
            update.message.reply_text(auth_data['error_message'])
        return

    session_row = {
        'username': post_data['username'],
        'token': auth_data["data"]["access_token"],
    }
    session_data = get_session(post_data['username'])
    log_debug(f'** login_handler.session_data: {session_data}')
    if session_data['error']:
        update.message.reply_text(session_data['error'])
        return
    if session_data['found']:
        # ?????
        # AttributeError: 'Session' object has no attribute '_id'
        # login_handler.session_data: {'error': False, 'error_message': None, 'resultset': {'_id': ObjectId('63d723d58499ee8663e78ebd'), 'username': 'tomkat_cr', 'token': 'xxxx'}, 'found': True, 'data': Session(username='tomkat_cr', token='xxxx')}
        # ?????
        # session_row['_id'] = session_data['data']._id
        # ?????
        session_row['_id'] = get_id_as_str(session_data['resultset'])
        response = update_session(session_row)
        log_debug(f'** login_handler.update_session.response: {response}')
        if response['resultset']['rows_affected'] == '0':
            update.message.reply_text(auth_messages.SESSION_NOT_UPDATED)
            return
    else:
        response = create_session(session_row)
        log_debug(f'** login_handler.create_session.response: {response}')
    if response['error']:
        update.message.reply_text(response['error_message'])
        return

    update.message.reply_text(auth_messages.AUTH_SUCCEED)
