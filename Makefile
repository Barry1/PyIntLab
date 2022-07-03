.PHONY: all pretty test install clean poetryupdate pyre build vermincheck mypy poetrypython poetrypypy
# https://www.gnu.org/software/make/manual/html_node/Setting.html#:~:text=The%20shell%20assignment%20operator%20%E2%80%98!%3D%E2%80%99
# OBJS=$(shell tree -if | egrep "\.pyi?$$")
#OBJS!=tree -if | egrep "\.pyi?$$"
#OBJS=$(shell find src -regex ".*\.pyi?$$")
OBJS!=find src -regex ".*\.pyi?$$"

monkeytype.sqlite3:
	niceload poetry run monkeytype run src/pyintlab/*.py

poetrypython:
	poetry env use python3.10
	poetry update

poetrypypy:
	poetry env use pypy
	poetry update

all: test

mypy:
	niceload poetry run mypy src/pyintlab

poetryupdate:
#	poetry self update
	niceload poetry check
	niceload poetry update

vermincheck: $(OBJS)
	niceload poetry run vermin -vv --backport typing $(OBJS)

pretty: $(OBJS)
	niceload poetry run isort $(OBJS)
	niceload poetry run black $(OBJS)
	niceload poetry run interrogate $(OBJS)

htmlcov/index.html: .coverage
	-niceload poetry run coverage3 report
	-niceload poetry run coverage3 html

pylama:
	-niceload poetry run pylama

test: pretty $(OBJS) pyright pyre htmlcov/index.html
# <https://archive.is/yoSpr>
# PEP8 is now pycodestyle which is included in pylama
# Simply speaking flake8 is “the wrapper which verifies pep8, pyflakes and circular complexity “
# look at <https://levelup.gitconnected.com/b9a9776a7871> = <https://archive.is/dbDPq>
# black
# eradicate
# vulture
# coverage
	-niceload poetry run pytest
	-niceload poetry run mypy --install-types --non-interactive $(OBJS)
	-niceload poetry run pylama $(OBJS)

build:
	niceload poetry build -f wheel -n

install:
#	python3 -m pip install --upgrade --user --progress-bar pretty --editable git+https://github.com/Barry1/PyIntLab#egg=pyintlab
	python3 -m pip install --upgrade --user --progress-bar pretty --editable /mnt/c/Users/der_b/Dokumente/GitHub/PyIntLab

clean:
	rm -rf pyintlab.egg-info dist

pyre:
	-niceload poetry run pyre
#	-pyre --noninteractive check
#	-mkdir -p pyre_analyze_results
	-niceload poetry run pyre --noninteractive analyze --save-results-to pyre_analyze_results --use-cache
	-niceload poetry run pyre --noninteractive statistics > pyre_statistics

pyright: export NODE_OPTIONS = --experimental-worker
pyright:
	@echo "==========" "$@" "=========="
	-niceload poetry run pyright --dependencies --stats --verbose $(OBJS)
	-niceload poetry run pyright
