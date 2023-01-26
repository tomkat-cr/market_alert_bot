import logging
import os
import requests
import datetime
import sys


from telegram.ext import Updater, CommandHandler
import serial.tools.list_ports
from a2wsgi import ASGIMiddleware


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# https://www.alphr.com/telegram-find-user-id/
TELEGRAM_CHAT_ID = ''


# BOT version


def get_bot_version():
    return os.environ.get('BOT_VERSION', '0.1.11')


# Debugging


def serial_ports():
    ports = serial.tools.list_ports.comports()
    result = []
    result.append(f'Platform: {sys.platform}')
    for port, desc, hwid in sorted(ports):
        result.append("{}: {} [{}]".format(port, desc, hwid))
    return result


# Telegram error reporting


def send_tg_message(user_id, message):
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    # Send the message
    url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + user_id + '&text=' + str(message)
    response = requests.get(url)
    print(response.content)
    return response


def report_error_to_tg_group(api_response):
    if not api_response['error']:
        return
    return send_tg_message(TELEGRAM_CHAT_ID, {
        'type': 'ERROR in a Mediabros API',
        'app_name': os.environ.get('APP_NAME', 'telegram-market-alert-bot'),
        'server_name': os.environ.get('SERVER_NAME'),
        'calling_func': sys._getframe(1).f_code.co_name,
        'error_message': api_response['error_message'],
    })


# Utility functions


def get_api_standard_response():
    standard_response = dict()
    standard_response['error'] = False
    standard_response['error_message'] = ''
    standard_response['data'] = dict()
    return standard_response

# ------------------------------------


# Mediabros API functions


def crypto_api(symbol, currency):
    api_response = get_api_standard_response()
    currency = currency.upper()
    symbol = symbol.upper()
    # url = 'https://min-api.cryptocompare.com/data/price?' + \
    # 'fsym=ETH&tsyms=BTC,USD,EUR'
    url = 'https://min-api.cryptocompare.com/data/price?' + \
        f'fsym={symbol}&tsyms={currency}'
    try:
        response = requests.get(url)
        # Ok response:
        # {'USD': 0.2741}
        # Error response:
        # {'Response': 'Error', 'Message': 'fsym is a required param.',
        # 'HasWarning': False, 'Type': 2, 'RateLimit': {}, 'Data': {},
        # 'ParamWithError': 'fsym'}
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code != 200:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading the ' + \
                'min-api.cryptocompare.com API'
        else:
            api_response['data'] = response.json()
            if api_response['data'].get('Response', '') == 'Error':
                api_response['error'] = True
                api_response['error_message'] = "ERROR: " + \
                    api_response['data']['Message']
    report_error_to_tg_group(api_response)
    return api_response


def veb_bcv_api():
    api_response = get_api_standard_response()
    url = 'https://bcv-exchange-rates.vercel.app/get_exchange_rates'
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            result = response.json()
            api_response['data'] = result
            if result['error']:
                api_response['error'] = True
                api_response['error_message'] = result['error_message']
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading BCV official' + \
                ' USD/Bs API'
    report_error_to_tg_group(api_response)
    return api_response


def veb_dolartoday_api():
    api_response = get_api_standard_response()
    url = 'https://s3.amazonaws.com/dolartoday/data.json'
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            api_response['data'] = response.json()
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading DolarToday API'
    report_error_to_tg_group(api_response)
    return api_response


def cop_api():
    api_response = get_api_standard_response()
    url = 'https://www.datos.gov.co/api/id/32sa-8pi3.json?' + \
        '$query=select%20*%2C%20%3Aid%20order%20by%20%60vigenciadesde' + \
        '%60%20desc%20limit%201'
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            api_response['data'] = response.json()
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading ' + \
                'datos.gov.co USD/COP API'
    report_error_to_tg_group(api_response)
    return api_response


# Middleware


def crypto(symbol, currency, debug):
    currency = currency.upper()
    symbol = symbol.upper()
    api_response = crypto_api(symbol, currency)
    if api_response['error']:
        response_message = api_response['error_message']
        if debug:
            response_message += f"\n{api_response['data']}"
        return response_message
    result = api_response['data']
    if debug:
        response_message = f'The {symbol} exchange rate is: {result}'
    else:
        exchange_rate = f'{float(result[currency]):.2f}' \
            if currency in result \
            else f"ERROR: no {currency} element in API result"
        response_message = f'The {symbol} to {currency} ' + \
            f'exchange rate is: {exchange_rate}'
    return response_message


def eth(debug):
    return crypto('eth', 'usd', debug)


def btc(debug):
    return crypto('btc', 'usd', debug)


def veb_bcv(debug):
    api_response = veb_bcv_api()
    if api_response['error']:
        return api_response['error_message']
    result = api_response['data']
    if debug:
        response_message = f'BCV official exchange rates: {result}'
    else:
        exchange_rate = float(result['data']['dolar']['value'])
        effective_date = result['data']['effective_date']
        response_message = 'BCV official exchange rate:' + \
            f' {exchange_rate:.2f} Bs/USD.\n' + \
            f'Effective Date: {effective_date}'
    return response_message


def veb_dolartoday(debug):
    api_response = veb_dolartoday_api()
    if api_response['error']:
        return api_response['error_message']
    result = api_response['data']
    if debug:
        response_message = f'DolarToday exchange rate: {result}'
    else:
        exchange_rate = float(result['USD']['transferencia'])
        from_date = result['_timestamp']['fecha_corta']
        response_message = 'DolarToday exchange rate:' + \
            f' {exchange_rate:.2f} Bs/USD.\n' + \
            f'Date: {from_date}'
    return response_message


def usdveb(debug):
    response_message = veb_bcv(debug)
    response_message += '\n\n' + veb_dolartoday(debug)
    return response_message


def usdcop(debug):
    api_response = cop_api()
    if api_response['error']:
        return api_response['error_message']
    result = api_response['data']
    if debug:
        response_message = f'The COP/USD exchange rate is: {result}'
    else:
        exchange_rate = float(result[0]['valor'])
        from_date = datetime.date.strftime(
            datetime.datetime.strptime(
                result[0]['vigenciadesde'],
                "%Y-%m-%dT%H:%M:%S.000"
            ), "%B %d, %Y"
        )
        to_date = datetime.date.strftime(
            datetime.datetime.strptime(
                result[0]['vigenciahasta'],
                "%Y-%m-%dT%H:%M:%S.000"
            ), "%B %d, %Y"
        )
        response_message = 'The COP exchange rate is: ' + \
            f'{exchange_rate:.2f} COP/USD.\n' + \
            f'From: {from_date}, to: {to_date}'
    return response_message


def veb_cop(currency_pair, debug):
    veb_response = veb_bcv_api()
    cop_response = cop_api()
    if veb_response['error']:
        return veb_response['error_message']
    if cop_response['error']:
        return cop_response['error_message']
    result = veb_response['data']
    if debug:
        response_message = f'BCV official: {veb_response["data"]}' + \
            '\n' + \
            f'COP official: {cop_response["data"]}'
    else:
        veb_exchange_rate = float(result['data']['dolar']['value'])
        effective_date = result['data']['effective_date']
        result = cop_response['data']
        cop_exchange_rate = float(result[0]['valor'])
        if currency_pair == 'copveb':
            exchange_rate = cop_exchange_rate / veb_exchange_rate
            suffix = 'COP/Bs'
        else:
            exchange_rate = veb_exchange_rate / cop_exchange_rate
            suffix = 'Bs/COP'
        response_message = 'Exchange rate:' + \
            f' {exchange_rate:.4f} {suffix}.\n' + \
            f'Effective Date: {effective_date}'
    return response_message


# ------------------------------------


# Command functions


def start(update, context):
    print('Command: /start')
    update.message.reply_text(
        'Hello! I\'m the Mediabros Market Alert BOT version '
        f'{get_bot_version()}.'
        '\nUse /help to get the command list.'
        '\nHow can I help you today baby?')


def help(update, context):
    print('Command: /help')
    update.message.reply_text(
        'Command Help:\n\n'
        '/help = get this documentation.\n'
        '\n'
        '/cur cop = same as /currency usdcop\n'
        '/currency usdcop = get the USD to COP (Colombian Peso)'
        ' exchange rate.\n'
        '\n'
        '/cur bs = same as /currency usdveb\n'
        '/cur veb = same as /currency usdveb\n'
        '/cur vef = same as /currency usdveb\n'
        '/currency usdveb = get the USD to VEB (Venezuelan Bolivar)'
        ' exchange rate.\n'
        '\n'
        '/cur copveb = get the COP/Bs exchange rate.\n'
        '/cur vebcop = get the Bs/COP exchange rate.\n'
        '\n'
        '/crypto [symbol] = get the crypto currency symbol exchange to USD.'
        ' [symbol] can be btc, eth, sol, ada, xrp, etc.\n'
        '\n'
        'NOTE: adding the word "debug" makes the command to return the API\'s'
        ' raw responses'
        '\n'
    )


def get_updates_debug(update, context):
    response = f'Update:\n{update}\nContext:\n{context}'
    update.message.reply_text(response)


def currency_exchange(update, context):
    # Get user's parameters

    # currency_pair = " ".join(context.args)
    currency_pair = context.args[0] if len(context.args) > 0 else ''
    currency_pair = currency_pair.lower()

    par2 = context.args[1] if len(context.args) > 1 else ''

    # Debug flag shows the raw responses
    debug = (par2.lower() == 'debug')

    print(f'Command: /currency {currency_pair} {debug}')

    # Select currency pair
    if currency_pair in ('usdcop', 'cop'):
        response_message = usdcop(debug)
    elif currency_pair in ('usdveb', 'veb', 'vef', 'bs'):
        response_message = usdveb(debug)
    elif currency_pair in ('usdbtc', 'btc'):
        response_message = btc(debug)
    elif currency_pair in ('usdeth', 'eth'):
        response_message = eth(debug)
    elif currency_pair in ('vebcop', 'copveb'):
        response_message = veb_cop(currency_pair, debug)
    else:
        # If invalid or missing currency pair code, report the error
        response_message = 'Please specify the currency pair.'
    update.message.reply_text(response_message)


def crypto_exchange(update, context):
    # Get user's parameters

    crypto_symbol = context.args[0] if len(context.args) > 0 else ''
    crypto_symbol = crypto_symbol.upper()

    par2 = context.args[1] if len(context.args) > 1 else ''

    # Debug flag shows the raw responses
    debug = (par2.lower() == 'debug')

    print(f'Command: /crypto {crypto_symbol} {debug}')

    # Select currency pair
    if crypto_symbol:
        response_message = crypto(crypto_symbol, 'usd', debug)
    else:
        # If invalid or missing crypto symbol, report the error
        response_message = 'Please specify the crypto currency symbol.'
    update.message.reply_text(response_message)


def main():

    bot_version = get_bot_version()

    bot_run_mode = os.environ.get('RUN_MODE', 'webhook')
    bot_listen_addr = os.environ.get('LISTEN_ADDR', '0.0.0.0')
    # -> Vercel: PermissionError: [Errno 13] Permission denied
    # bot_port = os.environ.get('PORT', '80')
    # <- Vercel: PermissionError: [Errno 13] Permission denied
    # bot_port = os.environ.get('PORT', '5000')
    bot_port = os.environ.get('PORT', '3000')
    bot_server_name = os.environ.get('SERVER_NAME', False)
    telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    global TELEGRAM_CHAT_ID
    TELEGRAM_CHAT_ID = os.environ.get(
        'TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID
    )

    # Updater creation
    updater = Updater(telegram_bot_token, use_context=True)

    # /start command
    updater.dispatcher.add_handler(CommandHandler('start', start))

    # /help command
    updater.dispatcher.add_handler(CommandHandler('help', help))

    # /currency command
    updater.dispatcher.add_handler(
        CommandHandler('currency', currency_exchange)
    )

    # /cur command
    updater.dispatcher.add_handler(CommandHandler('cur', currency_exchange))

    # /crypto command
    updater.dispatcher.add_handler(CommandHandler('crypto', crypto_exchange))

    # /get_updates command
    updater.dispatcher.add_handler(CommandHandler(
        'get_updates', get_updates_debug
    ))

    # Bot init
    print(f'Mediabros\' Market Alert BOT version {bot_version}')
    if bot_run_mode == 'cli':
        print('Start polling...')
        updater.start_polling(timeout=1600)
    else:
        print('Webhook mode...')
        print(f'bot_server_name [webhook_url]: {bot_server_name}')
        print(f'Listen to: {bot_listen_addr}:{bot_port}')
        if not bot_server_name:
            raise Exception("ERROR: Server Name variable not set")
        print('Starting webhook...')
        webhook = updater.bot.get_webhook_info()
        print(updater.bot.get_me())
        print(webhook)
        if webhook.url:
            print('delete_webhook...')
            updater.bot.delete_webhook()
            webhook = updater.bot.get_webhook_info()
        if not webhook.url:
            print('start_webhook...')
            updater.start_webhook(
                listen=bot_listen_addr,
                port=int(bot_port),
                webhook_url=f'{bot_server_name}',
                drop_pending_updates=True,
            )

    print('Ports report...')
    print(serial_ports())

    print(f'[{bot_run_mode}] Wait for requests...')
    updater.idle()

    if bot_run_mode == 'cli':
        return updater
    else:
        return ASGIMiddleware(updater)


handler = main()
