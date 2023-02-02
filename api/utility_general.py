# mediabros_utilities.py
import sys
import datetime
import serial.tools.list_ports
import traceback
import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
from .settings import settings


# Utility functions


def get_formatted_date():
    date_format = "%Y-%m-%d %H:%M:%S UTC"
    formatted_date = datetime.date.strftime(
        datetime.datetime.utcnow(), date_format
    )
    return formatted_date


def get_api_standard_response():
    standard_response = dict()
    standard_response['error'] = False
    standard_response['error_message'] = ''
    standard_response['data'] = dict()
    return standard_response


def get_command_line_args():
    params = dict()
    params['mode'] = 'api'
    params['config_filename'] = '.env'
    if len(sys.argv) > 1:
        params['mode'] = sys.argv[1]
    if len(sys.argv) > 2:
        params['config_filename'] = sys.argv[2]
    if len(sys.argv) > 3:
        params['body'] = ' '.join(
            [sys.argv[i] for i in range(3, len(sys.argv))]
        )
    return params


# Debugging


def serial_ports():
    ports = serial.tools.list_ports.comports()
    result = []
    result.append(f'Platform: {sys.platform}')
    for port, desc, hwid in sorted(ports):
        result.append("{}: {} [{}]".format(port, desc, hwid))
    return result


def log_endpoint_debug(log_msg):
    print('---------')
    print(get_formatted_date())
    print(log_msg)


def log_debug(message):
    if settings.DEBUG:
        print("[DEBUG] {} | {}".format(datetime.datetime.now(), message))


def log_warning(message):
    print("[WARNING] {} | {}".format(datetime.datetime.now(), message))


def log_normal(message):
    print(message)


def format_stacktrace():
    parts = ["Traceback (most recent call last):\n"]
    parts.extend(traceback.format_stack(limit=25)[:-2])
    parts.extend(traceback.format_exception(*sys.exc_info())[1:])
    return "".join(parts)


# Database


def get_default_db_resultset():
    resultset = {
        'error': False,
        'error_message': None,
        'resultset': {}
    }
    return resultset


def get_standard_base_exception_msg(err, message_code='NO_E_CODE'):
    """When a BaseException is fired, use this method to return
    a standard error message"""
    message_code = f"[{message_code=}]" if message_code == '' else ''
    response = f"Unexpected {err=}, {type(err)=} {message_code=}"
    log_normal(response)
    log_normal(format_stacktrace())
    return response


# API calls


def generic_api_call(url, api_name, post_data=None, headers=None):
    api_response = generic_api_call_raw(url, api_name, post_data, headers)
    if 'data' in api_response and \
       'error' in api_response and \
       'error_message' in api_response:
        if not api_response['error']:
            return str(api_response['data'])
    return str(api_response)


def generic_api_call_raw(
    url, api_name, post_data=None, headers=None, body=None
):
    log_endpoint_debug(f'>>--> GENERIC_API_CALL: {api_name}')
    log_normal('-------------')
    log_normal(f'URL: {url}')
    log_normal(f'post_data: {post_data}')
    log_normal(f'headers: {headers}')

    api_response = get_api_standard_response()
    api_response['response.status_code'] = None
    api_response['response.text'] = None
    try:
        if post_data or headers or body:
            headers = headers if headers is not None else dict()
            if post_data:
                data = json.dumps(post_data)
                headers['Content-type'] = 'application/json'
                print(
                    f'API call [POST/post_data]: data={data},' +
                    f' headers={headers}'
                )
                response = requests.post(
                    url,
                    data=data,
                    headers=headers
                )
            elif body:
                data = MultipartEncoder(fields=body)
                headers['Content-type'] = data.content_type
                print(f'API call [POST/body]: data={data}, headers={headers}')
                response = requests.post(
                    url,
                    data=data,
                    headers=headers
                )
            else:
                print(f'API call [POST/only headers]: headers={headers}')
                response = requests.post(
                    url,
                    headers=headers
                )
        else:
            print(f'API call [GET]: url={url}')
            response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        api_response['response.status_code'] = response.status_code
        api_response['response.text'] = response.text
        if response.status_code == 200:
            if 'error' not in response and 'data' not in response:
                api_response['data'] = response.json()
            else:
                api_response = response.json()
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading ' + \
                f'{api_name} API.' + \
                f' Status: {response.status_code}, Text: {response.text}'
    log_normal('-------------')
    log_normal(f'API call RESPONSE: {api_response}')
    return api_response
