# market_alert_bot
Telegram Market Alert BOT in Python.
This BOT shows the currency conversion of COP (Colombian Pesos) and VEB (Venezuelan Bs) to US Dollars, and any Crypto currency value in US Dollar.

## Requirements

- git
- Python 3.11
- fly.io
- ngrok

## How to use the BOT

- Go to Telegram and search for: `ocr_marketalert`
- Double click on the `@ocr_marketalert_bot` entry
- Click on the `Start` link at the bottom of the chat section.
- Use `/help` to get the command list.

## How to use the repo

- Open a Terminal window.
- Change to the parent directory you use to store your repos.
- Then run these commands:

```bash
git clone https://github.com/tomkat-cr/market_alert_bot.git
cd market_alert_bot
```

- All the magic is in the `index.py` file on the `api` directory...

## Installation

- Run this command:

```bash
make install
```

## How to deploy to fly.io

Create the BOT on Telegram:

- Go to Telegram
- Search for: `botfather`
- Double click on the `@botfather` entry
- Click on the `Start` link at the bottom of the chat section.
- Use `/newbot` command to create the BOT.
- Follow on-screen instructions to assign a BOT user name, BOT name, etc. Please use a different name than `@ocr_marketalert_bot` ;)
- That the end of the process, copy the Telegram BOT Token and store it in a secure place.

Create the .env file:

- Run this command:

```bash
cp .env-example .env
```

- Edit the `.env` file and paste the Telegram BOT Token on the `TELEGRAM_BOT_TOKEN` variable.

Create the App on [Fly.io](https://fly.io) by running this command:

```bash
sh run_fly_io.sh create_app
```

Finally deploy it running this command:

```bash
sh run_fly_io.sh deploy
```

NOTE:<br/>
The `api/Dockerfile` has the magic to run the BOT on [Fly.io](https://fly.io). It creates a docker container with python setup, perform a `pip install` and run `python index.py`. That's the way Fly.io works.<br/><br/>

## BOT local running in Polling mode

Use the Polling mode when you can use a server that allow constant running of the python app.

- Edit the `.env` file and un-comment this line:

```
# RUN_MODE=cli
```

- Run these commands:

```bash
sh run_fly_io.sh run
```

## BOT local running in Webhook mode

Use the Webhook mode when you need to deploy the BOT as a serverless function.

- Edit the `.env` file and comment this line by adding a `#` as a first character:

```
RUN_MODE=cli
```

- Run these commands:

```bash
npm install --also=dev
sh run_fly_io.sh run_ngrok
```

- A screen like this will appear:

```
Session Status                online
Session Expires               1 hour, 52 minutes
Version                       2.3.40
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://6272-190-73-192-124.ngrok.io -> http://localhost:8000
Forwarding                    https://6272-190-73-192-124.ngrok.io -> http://localhost:8000
```

- Copy se URL in the second `Forwarding`.
- Open a new Terminal window.
- Change the current directory to the one with the cloned repo `cd ./market_alert_bot`
- Run this command replacing `[FORWARDING_URL]` with the URL copied in a previous step:

```bash
sh run_fly_io.sh run_webhook [FORWARDING_URL]
```
- Go to Telegram and test your BOT.
- Enjoy!
