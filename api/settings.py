import os


class settings:
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    APP_NAME = os.environ.get('APP_NAME')
    SERVER_NAME = os.environ.get('SERVER_NAME', False)
    RUN_MODE = os.environ.get('RUN_MODE')
    APIS_COMMON_SERVER_NAME = os.environ.get('APIS_COMMON_SERVER_NAME')
    #
    LISTEN_ADDR = os.environ.get('LISTEN_ADDR', '0.0.0.0')
    # -> Vercel: PermissionError: [Errno 13] Permission denied
    # bot_port = os.environ.get('PORT', '80')
    # <- Vercel: PermissionError: [Errno 13] Permission denied
    # bot_port = os.environ.get('PORT', '5000')
    PORT = os.environ.get('PORT', '3000')
