import urllib.parse


from .settings import settings
from .utility_general import generic_api_call, generic_api_call_raw
from .utility_auth import auth_messages


# Exchange APIs


def crypto(symbol, currency, debug):
    debug = "1" if debug else "0"
    currency = currency.upper()
    symbol = symbol.upper()
    url = settings.APIS_COMMON_SERVER_NAME + \
        f'/crypto_wc/{symbol}/{currency}/{str(debug)}'
    return generic_api_call(url, 'Crypto Currency Exchange')


def usdveb(debug):
    debug = "1" if debug else "0"
    url = settings.APIS_COMMON_SERVER_NAME + \
        f'/usdvef/{str(debug)}'
    return generic_api_call(url, 'Venezuelan Bolivar Exchange')


def usdcop(debug):
    debug = "1" if debug else "0"
    url = settings.APIS_COMMON_SERVER_NAME + \
        f'/usdcop/{str(debug)}'
    return generic_api_call(url, 'Colombian Peso Exchange')


def veb_cop(currency_pair, debug):
    debug = "1" if debug else "0"
    url = settings.APIS_COMMON_SERVER_NAME + \
        f'/{currency_pair}/{str(debug)}'
    return generic_api_call(
        url, f'Bolivar COP Exchange [{currency_pair}]'
    )


# AI


def openai_api(command, other_param, debug, post_data, headers):
    if post_data is None:
        post_data = dict()
    url = settings.APIS_COMMON_SERVER_NAME + f'{command}'
    post_data['debug'] = "1" if debug else "0"
    post_data['q'] = urllib.parse.quote(other_param)
    api_response = generic_api_call_raw(
        url, f'Open AI [{command}]', post_data=post_data, headers=headers
    )
    if api_response['response.status_code'] == 401:
        response = f'{auth_messages.AUTH_WITH_LOGIN_CMD}. [OAIA-010]'
    elif api_response['response.status_code'] == 400:
        response = f'{auth_messages.USER_INACTIVE}. [OAIA-020]'
    elif 'data' in api_response and api_response['data']:
        response = str(api_response['data'])
    elif 'response.text' in api_response:
        response = api_response['response.text'] + \
            f" [{str(api_response['response.status_code'])}]"
    else:
        response = f'{auth_messages.UNKNOWN_ERROR}. [OAIA-030]'
    return response
