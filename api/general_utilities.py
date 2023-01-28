# mediabros_utilities.py
import sys
import datetime
import serial.tools.list_ports


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
