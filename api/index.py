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


def get_bot_version():
    return os.environ.get('BOT_VERSION', '0.1.8')


def serial_ports():
    ports = serial.tools.list_ports.comports()
    result = []
    result.append(f'Platform: {sys.platform}')
    for port, desc, hwid in sorted(ports):
        result.append("{}: {} [{}]".format(port, desc, hwid))
    return result


def start(update, context):
    print('Command: /start')
    update.message.reply_text(
        'Hello! I\'m the Mediabros Market Alert bot version '
        f'{get_bot_version()}.'
        '\nUse /help to get the command list.'
        '\nHow can I help you today baby?')


def help(update, context):
    print('Command: /help')
    update.message.reply_text(
        'Command Help:\n\n'
        '/help = get this documentation.\n'
        '/currency usdcop = get the USD to COP (Colombian Peso)'
        ' exchange rate.\n'
        '/cur cop = same as /currency usdcop\n'
        '/currency usdveb = get the USD to VEB (Venezuelan Bolivar)'
        ' exchange rate.\n'
        '/cur veb = same as /currency usdveb\n'
        '/crypto [symbol] = get the crypto currency symbol exchange to USD.'
        ' [symbol] can be btc, eth, sol, ada, xrp, etc.\n'
        '\n'
        'NOTE: adding the word "debug" makes the command to return the API\'s'
        ' raw responses'
        '\n'
    )


def eth(debug):
    return crypto('eth', 'usd', debug)


def btc(debug):
    return crypto('btc', 'usd', debug)


def crypto(symbol, currency, debug):
    response_message = 'ERROR: unknown [CRYPTO-E-010]'
    currency = currency.upper()
    symbol = symbol.upper()
    # url = 'https://min-api.cryptocompare.com/data/price?' + \
    # 'fsym=ETH&tsyms=BTC,USD,EUR'
    url = 'https://min-api.cryptocompare.com/data/price?' + \
        f'fsym={symbol}&tsyms={currency}'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        result = response.json()
        if debug:
            response_message = f'The {symbol} exchange rate is: {result}'
        else:
            exchange_rate = f'{float(result[currency]):.2f}' \
                if currency in result \
                else f"ERROR: no {currency} element in API result"
            response_message = f'The {symbol} to {currency} ' + \
                f'exchange rate is: {exchange_rate}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the min-api.cryptocompare.com API'
    return response_message


def veb_bcv(debug):
    response_message = 'ERROR: unknown [VEB_DOLARTODAY-E-010]'
    url = 'https://bcv-exchange-rates.vercel.app/get_exchange_rates'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        result = response.json()
        if debug:
            response_message = f'BCV official exchange rates: {result}'
        else:
            exchange_rate = float(result['data']['dolar']['value'])
            effective_date = result['data']['effective_date']
            response_message = 'BCV official exchange rate:' + \
                f' {exchange_rate:.2f} Bs/USD.\n' + \
                f'Effective Date: {effective_date}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the BCV official USD/Bs API'
    return response_message


def veb_dolartoday(debug):
    response_message = 'ERROR: unknown [VEB_DOLARTODAY-E-010]'
    url = 'https://s3.amazonaws.com/dolartoday/data.json'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        result = response.json()
        if debug:
            response_message = f'DolarToday exchange rate: {result}'
        else:
            exchange_rate = float(result['USD']['transferencia'])
            from_date = result['_timestamp']['fecha_corta']
            response_message = 'DolarToday exchange rate:' + \
                f' {exchange_rate:.2f} Bs/USD.\n' + \
                f'Date: {from_date}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the USD/Bs API'
    return response_message


def usdveb(debug):
    response_message = veb_bcv(debug)
    response_message += '\n\n' + veb_dolartoday(debug)
    return response_message


def usdcop(debug):
    response_message = 'ERROR: unknown [USDCOP-E-010]'
    url = 'https://www.datos.gov.co/api/id/32sa-8pi3.json?'
    '$query=select%20*%2C%20%3Aid%20order%20by%20%60vigenciadesde'
    '%60%20desc%20limit%201'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        # Si la llamada fue exitosa, obtenemos el objeto JSON
        result = response.json()
        if debug:
            response_message = f'The COP/USD exchange rate is: {result}'
        else:
            exchange_rate = float(result[0]['valor'])
            # To read the date/time string format, check this table:
            # https://docs.python.org/3.7/library/datetime.html#strftime-and-strptime-behavior
            # https://www.mytecbits.com/internet/python/string-to-datetime
            # https://www.mytecbits.com/internet/python/convert-date-to-mm-dd-yyyy
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
            # Python 3's f-Strings: `:.2f` to format float w/2 decimal places
            # https://realpython.com/python-f-strings/
            response_message = 'The COP exchange rate is: ' + \
                f'{exchange_rate:.2f} COP/USD.\n' + \
                f'From: {from_date}, to: {to_date}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the datos.gov.co USD/COP API'
    return response_message


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

    # Bot init
    print(f'Mediabros\' Market Alert bot version {bot_version}')
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
