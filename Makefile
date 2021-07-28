.PHONY: all pretty test install

OBJS=src/pyintlab/*.py

all: pretty test

pretty: $(OBJS)
	isort $(OBJS)
	black $(OBJS)
	interrogate $(OBJS)

test: pretty $(OBJS)
# <https://archive.is/yoSpr>
# PEP8 is now pycodestyle which is included in pylama
# Simply speaking flake8 is “the wrapper which verifies pep8, pyflakes and circular complexity “
# look at <https://levelup.gitconnected.com/b9a9776a7871> = <https://archive.is/dbDPq>
# black
# eradicate
# vulture
# coverage
	-pytest
	-mypy $(OBJS)
	-pylama $(OBJS)

install:
#	python3 -m pip install --upgrade --user --progress-bar pretty --editable git+https://github.com/Barry1/PyIntLab#egg=pyintlab
	python3 -m pip install --upgrade --user --progress-bar pretty --editable /mnt/c/Users/der_b/Dokumente/GitHub/PyIntLab
