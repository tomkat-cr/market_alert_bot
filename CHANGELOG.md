# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## 1.1.1 (2025-07-31)
---

### Changes
- Enhance README with detailed setup instructions and API documentation in both English and Spanish [GS-204].
- ".gitignore" to include IDE configurations [GS-204].
- Modify .nvmrc for Node.js version 20 [GS-219].
- Update Python version 3.13 [GS-219].


## 1.1.0 (2025-07-28)
---

### New
- CHANGELOG file added with commit history up to v1.0.1.
- Makefile file added.
- Add /veb command to get ONLY the official USD to VEB (Venezuelan Bolivar) exchange rate from the Central Bank (BCV) [GS-204].
- Add /mon command to get the USD to VEB from MonitorDolarVenezuela [GS-204].
- Add /bsf command to get both the official USD to VEB + MonitorDolarVenezuela [GS-204].
- Add the /usdveb_full and /usdveb_monitor mediabros_apis API calls [GS-204].
- Add "update" option to run_fly_io.sh to update dependencies versions, requirements.txt and venv [GS-219].
- Add "set_var_api_endpoint" option to run_fly_io.sh to set APIS_COMMON_SERVER_NAME only [GS-204].

### Changes
- Update telegram bot api calling to the latest version [GS-204].
- Change /vef to /veb in the mediabros_apis API call [GS-204].
- Update Dockerfile and local development to use Python 3.13 [GS-219].
- Improve dependency management in deployment scripts [GS-204].

### Fixes
- requirements.txt updated to solve snyk vulnerabilities [GS-219].
- run_fly_io.sh: clean change dir to api before running [GS-204].
- Fix "run_docker" and "run_webhook" Makefile entries with the correct execution parameter for "./run_fly_io.sh" [GS-204].
- Fix "run_ngrok" replacing "./node_modules/ngrok/bin/ngrok..." with "npx ngrok http $PORT" [GS-204].

### Breaks
- The /veb command does not include the DolarToday data as mediabros_apis API deprecated it [GS-204].


## 1.0.0 (2023-02-05)
---

### Fixes
- APIS_COMMON_SERVER_NAME taken from .env


## 0.1.8 (2023-02-04)
---

### Fixes
- Catch JSONDecodeError on generic_api_call_raw
- Replace endpoint /crypto_wc by /crypto_wc
- Flake8 warnings


## 0.1.7 (2023-02-01)
---

### New
- JWT token auth for /ai /codex

### Fixes
- /commands on any case (lower, upper, mixed
- get currency responses without debug in plain text, not json


## 0.1.6 (2023-01-28)
---

### New
- Fly.io restart


## 0.1.6 (2023-01-28)
---

### New
- Version increase & separate vars assign on gly.io
- Consume mediabros_apis
- Separate spurce .py files and import relative dirs
- /ai and /codex OpenAi interface


## 0.1.5 (2023-01-26)
---

### New
- README hints about Fly.io Dockerfile
- Test handle to run.sh
- npm commands to package.json

### Fixes
- OWNER -> TELEGRAM_CHAT_ID


## 0.1.4 (2023-01-06)
---

### New
- OWNER secret var set to fly.io
- Error reporting to telegram group or user_id
- `vebcop` and `copveb` currency pairs
- Error handling in all API calls
- `get_updates_debug` function to get group ID
- BCV official exchange rate initial launch

### Fixes
- `veb_bcv_api` url error


## 0.1.3 (2023-01-03)
---

### New
- Flake8 linting


## 0.1.2 (2022-12-31)
---

### New
- Instruction on README.md
- fly.io deployment and final hosting home
- `/crypto` command, local debug procedure

### Fixes
- Syntax errors fixed


## 0.1.1 (2022-12-30)
---

### New
- Initial commit 2022-12-30 CR
- Bot as a webhook
- Vercel config file
