# Makefile for python code
#
# > make help
#
# The following commands can be used.
#
# init:  sets up environment and installs requirements
# install:  Installs development requirments
# format:  Formats the code with autopep8
# lint:  Runs flake8 on src, exit if critical rules are broken
# clean:  Remove build and cache files
# env:  Source venv and environment files for testing
# leave:  Cleanup and deactivate venv
# test:  Run pytest
# run:  Executes the logic

# define the name of the virtual environment directory
VENV := .venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate:
	pip install  virtualenv
	virtualenv -p `which python2` .venv
	$(VENV)/bin/pip install -U pip==20.3.4
	# Used for packaging, linting and testing
	$(VENV)/bin/pip install setuptools wheel flake8 pytest
	$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

.PHONY: help
help:
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

.PHONY: install ## sets up environment and installs requirements
install: requirements.txt venv
	$(VENV)/bin/pip install -r requirements.txt


.PHONY: lint ## Runs flake8 on src, exit if critical rules are broken
lint: venv
	# stop the build if there are Python syntax errors or undefined names
	$(VENV)/bin/flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	$(VENV)/bin/flake8 src --count --exit-zero --statistics

SOURCE:=$(wildcard cos/*.py)
DIST_WHEEL=dist/coSentinel-%-py2-none-any.whl
DEPS_WHEELS=whls/%.whl
ALL_WHEELS=ansible/files/wheels/%.whl

$(DIST_WHEEL): $(SOURCE) requirements.txt venv
	$(VENV)/bin/python setup.py bdist_wheel --plat-name=any

$(ALL_WHEELS): $(DIST_WHEEL) requirements.txt
	mkdir -p ansible/files/wheels
	mv dist/*.whl ansible/files/wheels
	$(VENV)/bin/pip wheel -r requirements.txt -w ansible/files/wheels

build: $(ALL_WHEELS)

.PHONY: ansible
ansible: build
	ansible-playbook -i inventory/hosts.yaml ansible/site.yaml

.PHONY: clean ## Remove build and cache files
clean:
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	# Remove all pycache
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	# Remove all wheels
	rm -rf ansible/files/wheels

.PHONY: test ## Run pytest
test: init
	$(VENV)/bin/pytest . -p no:logging -p no:warnings
