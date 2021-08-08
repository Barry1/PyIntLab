.PHONY: all pretty test install clean poetryupdate
# https://www.gnu.org/software/make/manual/html_node/Setting.html#:~:text=The%20shell%20assignment%20operator%20%E2%80%98!%3D%E2%80%99
# OBJS=$(shell tree -if | egrep "\.pyi?$$")
OBJS!=tree -if | egrep "\.pyi?$$"

all: test

poetryupdate:
	poetry check
	poetry update

pretty: $(OBJS)
	poetry run isort $(OBJS)
	poetry run black $(OBJS)
	poetry run interrogate $(OBJS)

test: pretty $(OBJS) pyright
# <https://archive.is/yoSpr>
# PEP8 is now pycodestyle which is included in pylama
# Simply speaking flake8 is “the wrapper which verifies pep8, pyflakes and circular complexity “
# look at <https://levelup.gitconnected.com/b9a9776a7871> = <https://archive.is/dbDPq>
# black
# eradicate
# vulture
# coverage
	-poetry run pytest
	-poetry run mypy $(OBJS)
	-poetry run pylama $(OBJS)

install:
#	python3 -m pip install --upgrade --user --progress-bar pretty --editable git+https://github.com/Barry1/PyIntLab#egg=pyintlab
	python3 -m pip install --upgrade --user --progress-bar pretty --editable /mnt/c/Users/der_b/Dokumente/GitHub/PyIntLab

clean:
	rm -rf pyintlab.egg-info

pyre:
	-pyre
	-pyre --noninteractive check
	-mkdir -p pyre_analyze_results
	-pyre --noninteractive analyze --save-results-to pyre_analyze_results --use-cache
	-pyre --noninteractive statistics > pyre_statistics

pyright: export NODE_OPTIONS = --experimental-worker
pyright:
	@echo "==========" "$@" "=========="
	-pyright --dependencies --stats --verbose `tree -if | egrep "\.pyi?$$"`
	-pyright --verifytypes src/pyintlab
