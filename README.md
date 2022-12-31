# market_alert_bot
Telegram Market Alert Bot in Python

## How to use the Bot

- Go to Telegram and search for: `ocr_marketalert`
- Double click on the `@ocr_marketalert_bot` entry
- Click on the `Start` link at the bottom of the chat section.
- Use `/help` to get the command list.

## How to use the repo

Open a Terminal window.
Change to the parent directory you use to store your repos.
Then run these commands:

```bash
git clone https://github.com/tomkat-cr/market_alert_bot.git
cd market_alert_bot
```

All the magic is in the `api` directory...

## How to deploy to fly.io

Create the Bot on Telegram:

- Go to Telegram
- Search for: `botfather`
- Double click on the `@botfather` entry
- Click on the `Start` link at the bottom of the chat section.
- Use `/newbot` command to create the bot.
- Follow on-screen instructions to assign a bot user name, bot name, etc.
- In the bot name, use a different name than `@ocr_marketalert_bot` (please ;)
- That the end of the process, copy the Telegram Bot Token and store it in a secure place.

Create the .env file:

- Run this command:

```bash
cp .env-example .env
```

- Edit the `.env` file and paste the Telegram Bot Token on the 
`TELEGRAM_BOT_TOKEN` variable.

Create the App on [Fly.io](https://fly.io) by running this command:

```bash
sh run_fly_io.sh create_app
```

Finally deploy it running this command:

```bash
sh run_fly_io.sh deploy
```

## Bot local ruunning

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
sh run_fly_io.sh run_webhook `[FORWARDING_URL]`
```
- Go to Telegram and test your Bot.
- Enjoy!
