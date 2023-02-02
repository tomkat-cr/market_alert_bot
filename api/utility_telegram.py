import requests
import sys

from .settings import settings
from .utility_general import get_api_standard_response, log_normal, log_debug

# Telegram error reporting


def tg_base_url():
    bot_token = settings.TELEGRAM_BOT_TOKEN
    return f'https://api.telegram.org/bot{bot_token}/'


def tg_api_call(url):
    response = requests.get(url)
    log_normal(response.content)
    return response


def tg_delete_message(chat_id, message_id):
    url = tg_base_url() + 'deleteMessage?' + \
        'chat_id=' + str(chat_id) + '&message_id=' + str(message_id)
    return tg_api_call(url)


def tg_send_message(user_id, message):
    url = tg_base_url() + 'sendMessage?' + \
        'chat_id=' + str(user_id) + '&text=' + str(message)
    return tg_api_call(url)


def report_error_to_tg_group(api_response):
    if not api_response['error']:
        return
    return tg_send_message(settings.TELEGRAM_CHAT_ID, {
        'type': 'ERROR in a Mediabros API',
        'app_name': settings.APP_NAME,
        'server_name': settings.SERVER_NAME,
        'calling_func': sys._getframe(1).f_code.co_name,
        'error_message': api_response['error_message'],
    })


# Telegram command processing


def get_updates_debug(update, context):
    response = f'Update:\n{update}\nContext:\n{context}'
    update.message.reply_text(response)


def get_command_params(update, context):
    response = get_api_standard_response()
    del response['data']

    # Get user's command

    try:
        response['user'] = dict({
            'username': update['message']['chat'].username
        })
    except Exception as err:
        response['error'] = True
        response['error_message'] = \
            f'ERROR: Cannot retrieve the "from" element from Update.\n[{err}]'
        return response

    response['message_id'] = update['message']['message_id']
    response['chat_id'] = update['message']['chat']['id']

    try:
        response['text'] = update['message']['text']
    except Exception as err:
        response['error'] = True
        response['error_message'] = \
            f'ERROR: Cannot retrieve the "text" element from Update.\n[{err}]'
        return response

    if response['text'] is None:
        response['error'] = True
        response['error_message'] = 'ERROR: no text supplied.'
        return response

    try:
        response['command'] = response['text'].split(' ')[0].lower()
    except Exception as err:
        response['error'] = True
        response['error_message'] = \
            f'ERROR: command cannot be fetched.\n[{err}]'
        return response

    # Get user's parameters

    response['par'] = [
        context.args[i] for i in range(0, len(context.args))
    ]

    # Debug flag shows the raw responses
    response['debug'] = ('/debug' in response['par'])
    if response['debug']:
        response['par'].remove('/debug')

    log_debug(f'*** get_command_params.response: {response}')

    return response
