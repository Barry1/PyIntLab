.PHONY: all pretty test install

OBJS=pyintlab/*.py

all: pretty test

pretty: $(OBJS)
	isort $(OBJS)
	black $(OBJS)
	interrogate $(OBJS)

test: $(OBJS)
# <https://archive.is/yoSpr>
# PEP8 is now pycodestyle which is included in pylama
# Simply speaking flake8 is “the wrapper which verifies pep8, pyflakes and circular complexity “
	flake8 --max-line-length=88 $(OBJS)
	pytest
	mypy $(OBJS)
	-pylama $(OBJS)

install:
#	python3 -m pip install --upgrade --user --progress-bar pretty --editable git+https://github.com/Barry1/PyIntLab#egg=pyintlab
	python3 -m pip install --upgrade --user --progress-bar pretty --editable /mnt/c/Users/der_b/Dokumente/GitHub/PyIntLab
