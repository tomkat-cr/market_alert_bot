#!/bin/sh
# run_fly_io.sh
# 2022-12-31 | CR
#

run_deactivate() {
    cd ${APP_DIR} ;
    deactivate ;
    cd ..
}

run_clean() {
    cd "${APP_DIR}"
    pwd
    echo "Cleaning..."
    # deactivate ;
    rm -rf __pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf pyvenv.cfg ;
    rm -rf ../.vercel/cache ;
    ls -lah
    cd ..
}

run_fresh_install() {
    pip install python-telegram-bot
    pip install pyserial
    pip install a2wsgi
    pip install requests-toolbelt
    pip install pymongo
    pip install pydantic
    pip install werkzeug
    pip install setuptools
    pip freeze > requirements.txt
    # Add setuptools to requirements.txt if not already there
    if ! grep -q "setuptools" requirements.txt; then
        echo "setuptools>=70.0.0 # not directly required, pinned by Snyk to avoid a vulnerability" >> requirements.txt
    fi
}

run_venv() {
    pwd
    python3 -m venv ${APP_DIR} ;
    . ${APP_DIR}/bin/activate ;
    cd ${APP_DIR} ;
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        run_fresh_install
    fi
}

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
    run_deactivate
fi

if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" && "$1" != "set_webhook" && "$1" != "update" ]]; then
    run_venv
fi

if [ "$1" = "pipfile" ]; then
    # deactivate ;
    pipenv lock
fi

if [ "$1" = "clean" ]; then
    run_clean
fi

if [ "$1" = "update" ]; then
    rm "${APP_DIR}/requirements.txt"
    run_clean
    run_venv
    run_deactivate
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
fi

if [[ "$1" = "create_app" || "$1" = "set_vars" ]]; then
    echo "Setting: TELEGRAM_BOT_TOKEN = *****"
    flyctl secrets set TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    echo "Setting: TELEGRAM_CHAT_ID = ${TELEGRAM_CHAT_ID}"
    flyctl secrets set TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    echo "Setting: SERVER_NAME = ${SERVER_NAME}"
    flyctl secrets set SERVER_NAME=${FLYIO_APP_NAME}.fly.dev
    echo "Setting: RUN_MODE = cli"
    flyctl secrets set RUN_MODE=cli
    echo "Setting: APIS_COMMON_SERVER_NAME = ${APIS_COMMON_SERVER_NAME}"
    flyctl secrets set APIS_COMMON_SERVER_NAME=${APIS_COMMON_SERVER_NAME}
    echo "Setting: DB_URI = *******"
    flyctl secrets set DB_URI=${DB_URI}
    echo "Setting: DB_NAME = ${DB_NAME}"
    flyctl secrets set DB_NAME=${DB_NAME}
fi

if [ "$1" = "restart" ]; then
    flyctl apps restart ${FLYIO_APP_NAME} ;
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
    python -m ${APP_DIR}.index
fi

if [ "$1" = "run_webhook" ]; then
    if [ "$2" != "" ]; then
        SERVER_NAME=$2
        sh ../run_fly_io.sh set_webhook $2
    fi
    # python index.py
    cd ..
    python -m ${APP_DIR}.index
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
