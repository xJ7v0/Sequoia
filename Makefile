.DEFAULT_GOAL := default

FILES_TO_TAR := $(shell find . -type f -not -path './venv/*' -not -path './__pycache__/*' -not -name 'cpu' -not -name 'config.json')

default:
	tar --exclude='venv' --exclude='__pycache__' --exclude="cpu" --exclude="config.json" --exclude="robinhood.pickle" -zcvf /tmp/tradebot.tar.xz .

upload:
	curl -F'file=@/tmp/tradebot.tar.xz' -Fexpires=72 https://0x0.st
