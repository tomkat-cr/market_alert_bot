import logging
import os
# import requests
# import datetime

from telegram.ext import Updater, CommandHandler
from a2wsgi import ASGIMiddleware

from .general_utilities import serial_ports
from .settings import settings
from .general_utilities import get_api_standard_response
from .ext_api_processing import usdcop, usdveb, veb_cop, crypto, openai_api


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# BOT version


def get_bot_version():
    return os.environ.get('BOT_VERSION', '0.1.11')


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
        '/cop = get the USD to COP (Colombian Peso)'
        ' exchange rate.\n'
        '/cur cop = same as /cop\n'
        '/currency usdcop = same as /cop\n'
        '\n'
        '/bs = get the USD to VEB (Venezuelan Bolivar)'
        ' exchange rate.\n'
        '/cur bs = same as /bs\n'
        '/cur veb = same as /bs\n'
        '/cur vef = same as /bs\n'
        '/currency usdveb = same as /bs\n'
        '\n'
        '/copveb = get the COP/Bs exchange rate.\n'
        '/cur copveb = same as /copveb\n'
        '/vebcop = get the Bs/COP exchange rate.\n'
        '/cur vebcop = same as /vebcop\n'
        '\n'
        '/crypto [symbol] [currency] = get the crypto currency exchange to'
        ' to the specified currency (USD by default).\n'
        ' [symbol] can be btc, eth, sol, ada, xrp, etc.\n'
        ' [currency] can be USD, EUR, etc.\n'
        '\n'
        'NOTE: adding "/debug" makes the command to return the API\'s'
        ' raw responses.'
        '\n'
    )


def get_updates_debug(update, context):
    response = f'Update:\n{update}\nContext:\n{context}'
    update.message.reply_text(response)


def get_command_params(update, context):
    response = get_api_standard_response()
    del response['data']

    # Get user's command

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
        response['command'] = response['text'].split(' ')[0]
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

    return response


def currency_exchange(update, context):
    cmd_par = get_command_params(update, context)
    if cmd_par['error']:
        update.message.reply_text(cmd_par['error_message'])
        return

    currency_pair = ''
    if cmd_par['command'] == '/bs':
        currency_pair = 'usdveb'
    elif cmd_par['command'] == '/cop':
        currency_pair = 'usdcop'
    elif cmd_par['command'] == '/vebcop':
        currency_pair = 'vebcop'
    elif cmd_par['command'] == '/copveb':
        currency_pair = 'copveb'
    elif cmd_par['command'] == '/eth':
        currency_pair = 'eth'
    elif cmd_par['command'] == '/btc':
        currency_pair = 'btc'
    elif len(cmd_par['par']) > 0:
        currency_pair = cmd_par['par'][0].lower()
        cmd_par['par'].remove(cmd_par['par'][0])

    amount = 1.00
    if len(cmd_par['par']) > 0:
        try:
            amount = float(cmd_par['par'][0])
        except Exception:
            pass
        cmd_par['par'].remove(cmd_par['par'][0])

    print(
        f"Command: {cmd_par['text']} |" +
        f" {currency_pair} {amount} {cmd_par['debug']}"
    )

    # Select currency pair
    if currency_pair in ('usdcop', 'cop'):
        response_message = usdcop(cmd_par['debug'])
    elif currency_pair in ('usdveb', 'veb', 'vef', 'bs'):
        response_message = usdveb(cmd_par['debug'])
    elif currency_pair in ('usdbtc', 'btc'):
        response_message = crypto('btc', 'usd', cmd_par['debug'])
    elif currency_pair in ('usdeth', 'eth'):
        response_message = crypto('eth', 'usd', cmd_par['debug'])
    elif currency_pair in ('vebcop', 'copveb'):
        response_message = veb_cop(currency_pair, cmd_par['debug'])
    else:
        # If invalid or missing currency pair code, report the error
        response_message = 'Please specify a valid currency pair.'
    update.message.reply_text(response_message)


def crypto_exchange(update, context):
    cmd_par = get_command_params(update, context)
    if cmd_par['error']:
        update.message.reply_text(cmd_par['error_message'])
        return

    crypto_symbol = ''
    if len(cmd_par['par']) > 0:
        crypto_symbol = cmd_par['par'][0]
        crypto_symbol = crypto_symbol.upper()
        cmd_par['par'].remove(cmd_par['par'][0])

    currency = 'usd'
    if len(cmd_par['par']) > 0:
        currency = cmd_par['par'][0]
        cmd_par['par'].remove(cmd_par['par'][0])

    amount = 1.00
    if len(cmd_par['par']) > 0:
        try:
            amount = float(cmd_par['par'][0])
        except Exception:
            pass
        cmd_par['par'].remove(cmd_par['par'][0])

    print(
        f"Command: {cmd_par['command']} {crypto_symbol}" +
        f" {currency} {amount} {cmd_par['debug']}"
    )

    # Select currency pair
    if crypto_symbol:
        response_message = crypto(crypto_symbol, currency, cmd_par['debug'])
    else:
        # If invalid or missing crypto symbol, report the error
        response_message = 'Please specify the crypto currency symbol.'
    update.message.reply_text(response_message)


def ai_commands_handler(update, context):
    cmd_par = get_command_params(update, context)
    if cmd_par['error']:
        update.message.reply_text(cmd_par['error_message'])
        return

    other_param = ' '.join(cmd_par['par'])
    update.message.reply_text(
        openai_api(
            cmd_par['command'], other_param, cmd_par['debug']
        )
    )


def main():

    bot_version = get_bot_version()

    bot_run_mode = settings.RUN_MODE
    bot_listen_addr = settings.LISTEN_ADDR
    bot_port = settings.PORT
    bot_server_name = settings.SERVER_NAME
    telegram_bot_token = settings.TELEGRAM_BOT_TOKEN

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

    # Currency shortcuts
    updater.dispatcher.add_handler(CommandHandler('bs', currency_exchange))
    updater.dispatcher.add_handler(CommandHandler('cop', currency_exchange))
    updater.dispatcher.add_handler(CommandHandler('vebcop', currency_exchange))
    updater.dispatcher.add_handler(CommandHandler('copveb', currency_exchange))
    updater.dispatcher.add_handler(CommandHandler('btc', currency_exchange))
    updater.dispatcher.add_handler(CommandHandler('eth', currency_exchange))

    # /crypto command
    updater.dispatcher.add_handler(CommandHandler('crypto', crypto_exchange))

    # /ai & /codex commands
    updater.dispatcher.add_handler(
        CommandHandler('ai', ai_commands_handler)
    )
    updater.dispatcher.add_handler(
        CommandHandler('codex', ai_commands_handler)
    )

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
