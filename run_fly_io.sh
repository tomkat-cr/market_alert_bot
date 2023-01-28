#!/bin/sh
# run_fly_io.sh
# 2022-12-31 | CR
#
APP_DIR='api'
if [ -f "./.env" ]; then
    ENV_FILESPEC="./.env"
else
    ENV_FILESPEC="../.env"
fi
set -o allexport; source ${ENV_FILESPEC}; set +o allexport ;
if [ "$PORT" = "" ]; then
    PORT="8000"
fi
if [ "$1" = "deactivate" ]; then
    cd ${APP_DIR} ;
    deactivate ;
fi
if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" && "$1" != "set_webhook" ]]; then
    python3 -m venv ${APP_DIR} ;
    . ${APP_DIR}/bin/activate ;
    cd ${APP_DIR} ;
    pip3 install -r requirements.txt ;
fi
if [ "$1" = "pipfile" ]; then
    deactivate ;
    pipenv lock
fi
if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf pyvenv.cfg ;
    ls -lah
fi

if [[ "$1" = "test" ]]; then
    # echo "Error: no test specified" && exit 1
    echo "Run test..."
    python -m pytest
    echo "Done..."
fi

if [ "$1" = "create_app" ]; then
    flyctl auth login
    flyctl apps create ${FLYIO_APP_NAME}
    flyctl secrets set TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    flyctl secrets set TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    flyctl secrets set SERVER_NAME=${FLYIO_APP_NAME}.fly.dev
    flyctl secrets set RUN_MODE=cli
    flyctl secrets set APIS_COMMON_SERVER_NAME=https://mediabros-apis.vercel.app
fi

if [ "$1" = "deploy" ]; then
    flyctl deploy ;
fi
if [ "$1" = "deploy_prod" ]; then
    flyctl deploy ;
fi

if [ "$1" = "run_docker" ]; then
    docker-compose up -d
fi

if [ "$1" = "run_ngrok" ]; then
    ../node_modules/ngrok/bin/ngrok http $PORT
fi
if [ "$1" = "run" ]; then
    # python index.py
    cd ..
    python -m api.index
fi
if [ "$1" = "run_webhook" ]; then
    if [ "$2" != "" ]; then
        SERVER_NAME=$2
        sh ../run_fly_io.sh set_webhook $2
    fi
    # python index.py
    cd ..
    python -m api.index
fi
if [ "$1" = "set_webhook" ]; then
    # curl -X POST https://api.telegram.org/bot<YOUR-BOT-TOKEN>/setWebhook -H "Content-type: application/json" -d '{"url": "https://project-name.username.vercel.app/api/webhook"}'
    BOT_URL="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}"
    # D_PARAM="{\"url\": \"${SERVER_NAME}/${TELEGRAM_BOT_TOKEN}\"}";
    if [ "$2" = "" ]; then
        D_PARAM="{\"url\": \"${SERVER_NAME}\"}";
    else
        D_PARAM="{\"url\": \"$2\"}";
    fi
    echo ""
    echo $BOT_URL ;
    echo $D_PARAM ;
    echo $SERVER_NAME ;
    echo ""
    echo "setWebhook"
    curl -X POST "${BOT_URL}/setWebhook" -H "Content-type: application/json" -d "${D_PARAM}"
    echo ""
    echo ""
    echo "getMe"
    curl -X POST "${BOT_URL}/getMe"
    echo ""
    echo ""
fi
