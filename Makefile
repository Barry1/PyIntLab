.PHONY: all pretty test

OBJS=pyintlab/*.py

all: pretty test

pretty:
	isort $(OBJS)
	black $(OBJS)
	interrogate $(OBJS)

test:
# <https://archive.is/yoSpr>
# PEP8 is now pycodestyle which is included in pylama
# Simply speaking flake8 is “the wrapper which verifies pep8, pyflakes and circular complexity “
	flake8 --max-line-length=88 $(OBJS)
	pytest
	mypy $(OBJS)
	-pylama $(OBJS)
