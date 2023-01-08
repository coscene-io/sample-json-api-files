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

VENV_PATH='env/bin/activate'
ENVIRONMENT_VARIABLE_FILE='.env'

define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

.PHONY: help
help:
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

.PHONY: install ## sets up environment and installs requirements
install: requirements.txt
	pip install -r requirements.txt

.PHONY: init ## Installs development requirements
init:
	python -m pip install --upgrade pip
	# Used for packaging and publishing
	pip install setuptools wheel
	# Used for linting
	pip install flake8
	# Used for testing
	pip install pytest

.PHONY: lint ## Runs flake8 on src, exit if critical rules are broken
lint: init
	# stop the build if there are Python syntax errors or undefined names
	flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 src --count --exit-zero --statistics

.PHONY: pre-ansible ## Create package and upload to pypi
pre-ansible: requirements.txt
	mkdir -p ansible/files/wheels
	python setup.py bdist_wheel --plat-name=any
	cp dist/*.whl ansible/files/wheels
	pip wheel -r requirements.txt -w ansible/files/wheels

.PHONY: ansible
ansible: pre-ansible
	ansible-playbook -i ansible/inventory/hosts.yaml ansible/site.yaml

.PHONY: clean ## Remove build and cache files
clean:
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	# Remove all pycache
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

.PHONY: test ## Run pytest
test: init
	pytest . -p no:logging -p no:warnings
