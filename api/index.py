import logging
import os
import requests
import datetime

from telegram.ext import Updater, CommandHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    print('Command: /start')
    update.message.reply_text('Hello! I''m the Mediabros'' Market Alert bot. Use /help to get the command list. How can I help you today baby?')


def help(update, context):
    print('Command: /help')
    update.message.reply_text(
        'Command Help:\n\n'
        '/help = get this documentation.\n'
        '/currency usdcop = get the USD to COP (Colombian Peso) exchange rate.\n'
        '/currency usdveb = get the USD to VEB (Venezuelan Bolivar) exchange rate.\n'
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
    # url = f'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR'
    url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        result = response.json()
        if debug:
            response_message = f'The {symbol} exchange rate is: {result}'
        else:
            exchange_rate = f'{float(result[currency]):.2f}' if currency in result else f"ERROR: no {currency} element in API result"
            response_message = f'The {symbol} to {currency} exchange rate is: {exchange_rate}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the min-api.cryptocompare.com API'
    return response_message


def usdveb(debug):
    response_message = 'ERROR: unknown [USDVEB-E-010]'
    url = f'https://s3.amazonaws.com/dolartoday/data.json'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        result = response.json()
        if debug:
            response_message = f'The VEB/USD exchange rate is: {result}'
        else:
            exchange_rate = float(result['USD']['transferencia'])
            from_date = result['_timestamp']['fecha_corta']
            response_message = f'The Bs exchange rate is: {exchange_rate:.2f} Bs/USD.\nDate: {from_date}'
    else:
        # Report to user for API call error
        response_message = 'ERROR reading the USD/Bs API'
    return response_message


def usdcop(debug):
    response_message = 'ERROR: unknown [USDCOP-E-010]'
    url = f'https://www.datos.gov.co/api/id/32sa-8pi3.json?$query=select%20*%2C%20%3Aid%20order%20by%20%60vigenciadesde%60%20desc%20limit%201'
    response = requests.get(url)

    # Process result
    if response.status_code == 200:
        # Si la llamada fue exitosa, obtenemos el objeto JSON
        result = response.json()
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
            response_message = f'The COP exchange rate is: {exchange_rate:.2f} COP/USD.\nFrom: {from_date}, to: {to_date}'
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

    print(f'Command: /currency {currency_pair}')

    # Select currency pair
    if currency_pair in ('usdcop', 'cop'):
        response_message = usdcop(debug)
    elif currency_pair in ('usdveb', 'veb', 'vef'):
        response_message = usdveb(debug)
    elif currency_pair in ('usdbtc', 'btc'):
        response_message = btc(debug)
    elif currency_pair in ('usdeth', 'eth'):
        response_message = eth(debug)
    else:
        # If invalid or missing currency pair code, report the error
        response_message = 'Please specify the currency pair.'
    update.message.reply_text(response_message)


def main():

    bot_run_mode = os.environ.get('RUN_MODE', 'webhook')
    bot_port = os.environ.get('PORT', '443')
    bot_server_name = os.environ.get('SERVER_NAME', False)
    telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    # Updater creation with Telegram bot access token
    updater = Updater(telegram_bot_token, use_context=True)

    # Start command
    updater.dispatcher.add_handler(CommandHandler('start', start))

    # Start command
    updater.dispatcher.add_handler(CommandHandler('help', help))

    # Currency Exchange rates
    updater.dispatcher.add_handler(CommandHandler('currency', currency_exchange))

    # Bot init
    if bot_run_mode == 'cli':
        print('Start polling...')
        updater.start_polling(timeout=1600)
    else:
        print('Webhook mode...')
        print(f'bot_server_name: {bot_server_name}:{bot_port}')
        if not bot_server_name:
            raise Exception("ERROR: Server Name variable for not set")
        print('Start webhook...')
        updater.start_webhook(
            listen='0.0.0.0',
            port=int(bot_port),
            url_path=telegram_bot_token,
            webhook_url=f'{bot_server_name}/{telegram_bot_token}',
        )
        # updater.bot.set_webhook(
        #     f'{bot_server_name}/{telegram_bot_token}'
        # )
    print('Wait for requests...')
    updater.idle()
    return updater


# if __name__ == '__main__':
app = main()
