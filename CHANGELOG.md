# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## Unreleased
## 1.1.0 (2025-05-17)
---

### New
CHANGELOG file added with commit history up to v1.0.1
Makefile file added
run_fly_io.sh: update option added to update requirements.txt and venv

### Fixes
requirements.txt updated to solve snyk vulnerabilities
run_fly_io.sh: clean change dir to api before running
Fix "run_docker" and "run_webhook"Makefile entries with the correct execution parameter for "./run_fly_io.sh".
Fix "run_ngrok" replacing "./node_modules/ngrok/bin/ngrok..." with "npx ngrok http $PORT".

## 1.0.0 (2023-02-05)
---

### Fixes
APIS_COMMON_SERVER_NAME taken from .env


## 0.1.8 (2023-02-04)
---

### Fixes
Catch JSONDecodeError on generic_api_call_raw
Replace endpoint /crypto_wc by /crypto_wc
Flake8 warnings


## 0.1.7 (2023-02-01)
---

### New
JWT token auth for /ai /codex

### Fixes
/commands on any case (lower, upper, mixed
get currency responses without debug in plain text, not json


## 0.1.6 (2023-01-28)
---

### New
Fly.io restart


## 0.1.6 (2023-01-28)
---

### New
Version increase & separate vars assign on gly.io
Consume mediabros_apis
Separate spurce .py files and import relative dirs
/ai and /codex OpenAi interface


## 0.1.5 (2023-01-26)
---

### New
README gints about Fly.io Dockerfile
Test handle to run.sh
npm commands to package.json

### Fixes
OWNER -> TELEGRAM_CHAT_ID


## 0.1.4 (2023-01-06)
---

### New
OWNER secret var set to fly.io
error reporting to telegram group or user_id
vebcop and copveb currency pairs
error handling in all API calls
get_updates_debug function to get group ID
BCV official exchange rate initial launch

### Fixes
veb_bcv_api url error


## 0.1.3 (2023-01-03)
---

### New
Flake8 liniting


## 0.1.2 (2022-12-31)
---

### New
Instruction on README.md
fly.io deployment and final hosting home
/crypto command, local debug procedure

### Fixes
Syntax errors fixed


## 0.1.1 (2022-12-30)
---

### New
Initial commit 2022-12-30 CR
Bot as a webhook
Vercel config file
