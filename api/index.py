import logging
import os

from telegram.ext import Updater, CommandHandler
from a2wsgi import ASGIMiddleware

from .utility_telegram import get_command_params, get_updates_debug
from .utility_general import serial_ports, log_endpoint_debug, log_normal
from .settings import settings
from .utility_auth import get_user_authentication, login_handler
from .api_processing import usdcop, usdveb, veb_cop, crypto, openai_api

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# BOT version


def get_bot_version():
    return os.environ.get('BOT_VERSION', '0.1.14')


# ------------------------------------


# Command functions


def start(update, context):
    log_endpoint_debug('Command: /start')
    update.message.reply_text(
        'Hello! I\'m the Mediabros Market Alert BOT version '
        f'{get_bot_version()}.'
        '\nUse /help to get the command list.'
        '\nHow can I help you today baby?')


def help(update, context):
    log_endpoint_debug('Command: /help')
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

    log_endpoint_debug(
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

    log_endpoint_debug(
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
    auth_data = get_user_authentication(cmd_par)
    if not auth_data['found'] or auth_data['error']:
        update.message.reply_text(auth_data['error_message'])
        return
    other_param = ' '.join(cmd_par['par'])
    update.message.reply_text(
        openai_api(
            cmd_par['command'],
            other_param,
            cmd_par['debug'],
            auth_data['userdata'],
            auth_data['headers']
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

    # /login
    updater.dispatcher.add_handler(CommandHandler('login', login_handler))

    # /get_updates command
    updater.dispatcher.add_handler(CommandHandler(
        'get_updates', get_updates_debug
    ))

    # Bot init
    log_normal(f'Mediabros\' Market Alert BOT version {bot_version}')
    if bot_run_mode == 'cli':
        log_normal('Start polling...')
        updater.start_polling(timeout=1600)
    else:
        log_normal('Webhook mode...')
        log_normal(f'bot_server_name [webhook_url]: {bot_server_name}')
        log_normal(f'Listen to: {bot_listen_addr}:{bot_port}')
        if not bot_server_name:
            raise Exception("ERROR: Server Name variable not set")
        log_normal('Starting webhook...')
        webhook = updater.bot.get_webhook_info()
        log_normal(updater.bot.get_me())
        log_normal(webhook)
        if webhook.url:
            log_normal('delete_webhook...')
            updater.bot.delete_webhook()
            webhook = updater.bot.get_webhook_info()
        if not webhook.url:
            log_normal('start_webhook...')
            updater.start_webhook(
                listen=bot_listen_addr,
                port=int(bot_port),
                webhook_url=f'{bot_server_name}',
                drop_pending_updates=True,
            )

    log_normal('Ports report...')
    log_normal(serial_ports())

    log_normal(f'[{bot_run_mode}] Wait for requests...')
    updater.idle()

    if bot_run_mode == 'cli':
        return updater
    else:
        return ASGIMiddleware(updater)


handler = main()
