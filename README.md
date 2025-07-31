# Market Alert Bot

![Market Alert BOT banner](./assets/market.alert.bot.telegram.banner-010.png)

[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](https://github.com/tomkat-cr/market_alert_bot)
[![Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Node.js Version](https://img.shields.io/badge/node-20-green)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-ISC-green.svg)](LICENSE)

## Overview

`Market Alert Bot` is a Telegram bot built with Python that provides real-time currency exchange rates and cryptocurrency prices. It can fetch the value of Colombian Pesos (COP) and Venezuelan Bolívares (VEB) against the US Dollar, as well as the price of any major cryptocurrency in USD.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Makefile Commands](#makefile-commands)
- [License](#license)
- [Contributing](#contributing)

## Features

- **Currency Conversion**: Get the latest exchange rates for COP and VEB to USD.
- **Cryptocurrency Prices**: Look up the current price of any cryptocurrency in USD.
- **Telegram Integration**: Easy-to-use commands directly within the Telegram app.
- **Deployable**: Ready for deployment on [Fly.io](https://fly.io) using Docker.

## Technologies

- **Backend**: Python
- **Deployment**: Docker, [Fly.io](https://fly.io)
- **Development**: Node.js (for `ngrok` tunneling)
- **Automation**: `make`

## Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

Make sure you have the following software installed on your system:

- [Python 3.13](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Make](https://www.gnu.org/software/make/)
- [Node.js 20](https://nodejs.org/)
- [flyctl](https://fly.io/docs/hands-on/install-flyctl/) (for deployment)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/tomkat-cr/market_alert_bot.git
    cd market_alert_bot
    ```

2.  **Set up your environment variables:**

    Create a `.env` file by copying the example file. You will need a Telegram Bot Token from BotFather.
    ```sh
    cp .env-example .env
    ```
    Then, edit the `.env` file and add your token:
    ```
    TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    ```

3.  **Install dependencies:**

    The `install` command will set up everything you need to run the bot.
    ```sh
    make install
    ```

4. **Dependencies update**

    Over the time, you may need to update the dependencies, specially to get covered from vulnerabilities. Run this command:

    ```bash
    make update
    ```

## Usage

This project uses a `Makefile` to streamline common tasks. Below are the available commands.

### Makefile Commands

| Command                  | Description                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------- |
| `make` or `make all`     | Displays the contents of the `Makefile`.                                           |
| `make install`           | Installs `flyctl` using Homebrew.                                                  |
| `make clean`             | Cleans the project from temporary files and directories.                           |
| `make update`            | Updates dependencies versions, requirements.txt and venv.                          |
| `make restart`           | Restarts the application on Fly.io.                                                |
| `make run`               | Runs the bot locally in polling mode.                                              |
| `make run_webhook`       | Runs the bot locally using webhooks.                                               |
| `make run_ngrok`         | Starts an `ngrok` tunnel for local webhook development.                            |
| `make run_docker`        | Builds and runs the Docker container locally.                                      |
| `make create_app`        | Creates a new application on Fly.io.                                               |
| `make set_vars`          | Sets environment variables on Fly.io from the local `.env` file.                   |
| `make set_webhook`       | Sets the Telegram webhook to the Fly.io app URL.                                   |
| `make deploy`            | Deploys the application to production on Fly.io.                                   |
| `make deactivate`        | Deactivates the virtual environment.                                               |

## How to use the BOT

- Go to [Telegram](https://telegram.org/) and search for: `ocr_marketalert`
- Double click on the `@ocr_marketalert_bot` entry
- Click on the `Start` link at the bottom of the chat section.
- Use `/help` to get the command list.

## How to deploy to fly.io

Create the BOT on Telegram:

- Go to [Telegram](https://telegram.org/)
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

## License

This project is licensed under the ISC License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## Credits

This project is developed and maintained by [Carlos J. Ramirez](https://github.com/tomkat-cr). For more information or to contribute to the project, visit [Market Alert BOT](https://github.com/tomkat-cr/market_alert_bot).

Happy Coding!
