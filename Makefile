.PHONY: deactivate pipfile clean update restart run_docker run_webhook set_webhook create_app set_vars run_ngrok run
SHELL := /bin/bash

# default show this file
all:
	@cat Makefile

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

run_ngrok:
	${SHELL} ./run_fly_io.sh run_ngrok

run:
	${SHELL} ./run_fly_io.sh run
