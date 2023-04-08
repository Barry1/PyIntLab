.PHONY: all pretty test install clean pyflakes pytype poetryupdate pyre build vermincheck mypy poetrypython poetrypypy pcktree
# https://www.gnu.org/software/make/manual/html_node/Setting.html#:~:text=The%20shell%20assignment%20operator%20%E2%80%98!%3D%E2%80%99
# OBJS=$(shell tree -if | egrep "\.pyi?$$")
#OBJS!=tree -if | egrep "\.pyi?$$"
#OBJS=$(shell find src -regex ".*\.pyi?$$")
OBJS!=find src -regex ".*\.pyi?$$"

pcktree:
	niceload poetry show --tree

monkeytype.sqlite3:
	niceload poetry run monkeytype run src/pyintlab/*.py

pyflakes:
	niceload poetry run pyflakes src

pytype:
	niceload poetry run pytype src

poetrypython:
	poetry env use python3.10
	poetry update

pyroma:
	poetry run pyroma .

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

pyanalyze:
	poetry run python -m pyanalyze src/pyintlab/scalar_interval.py

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

git-story_media/videos/1080p60/GitStory.mp4:
	nice -19 poetry run git-story --reverse --commits=50
git-story_media/videos/480p15/GitStory.mp4:
	nice -19 poetry run git-story --reverse --commits=50 --low-quality

aptprep:
	echo "For git-story"
	sudo apt-get install libcairo2-dev pkg-config python3-dev libpango1.0-dev
	sudo apt-get install libcairo2 libfontconfig1 libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 

workflowtest:
#time /home/ebeling/GitHub/bin/act --list | awk 'NR>1{print $2}' | parallel /home/ebeling/GitHub/bin/act --job > parallel.output
#time /home/ebeling/GitHub/bin/act --list | awk 'NR>1{print $2}' | xargs -P 4 -L 1 /home/ebeling/GitHub/bin/act --job > xargs.output
	/home/ebeling/GitHub/bin/act --list
	/home/ebeling/GitHub/bin/act --graph
	/home/ebeling/GitHub/bin/act 

alltoolchain: autopep8 flake8 mypy pycodestyle pydocstyle pyflakes pylama pylint pyright pytype

autopep8:
	poetry run autopep8 src/pyintlab/*.py

flake8:
	poetry run flake8 src/pyintlab/*.py

pycodestyle:
	poetry run pycodestyle src/pyintlab/*.py

pydocstyle:
	poetry run pydocstyle src/pyintlab/*.py

pylint:
	poetry run pylint src/pyintlab/*.py
