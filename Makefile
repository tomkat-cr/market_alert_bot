.PHONY: install deploy deploy_prod deactivate pipfile clean update restart run_docker run_webhook set_webhook create_app set_vars run_ngrok run
SHELL := /bin/bash

# default show this file
all:
	@cat Makefile

install:
	# https://github.com/superfly/flyctl
	brew install flyctl

deactivate:
	${SHELL} ./run_fly_io.sh deactivate

pipfile:
	${SHELL} ./run_fly_io.sh pipfile

clean:
	${SHELL} ./run_fly_io.sh clean

update:
	${SHELL} ./run_fly_io.sh update

restart:
	${SHELL} ./run_fly_io.sh restart

run_docker:
	${SHELL} ./run_fly_io.sh run_docker

run_webhook:
	${SHELL} ./run_fly_io.sh run_webhook

set_webhook:
	${SHELL} ./run_fly_io.sh set_webhook

create_app:
	${SHELL} ./run_fly_io.sh create_app

set_vars:
	${SHELL} ./run_fly_io.sh set_vars

set_var_api_endpoint:
	${SHELL} ./run_fly_io.sh set_var_api_endpoint

run_ngrok:
	${SHELL} ./run_fly_io.sh run_ngrok

run:
	${SHELL} ./run_fly_io.sh run

deploy_prod:
	${SHELL} ./run_fly_io.sh deploy_prod

deploy: deploy_prod
