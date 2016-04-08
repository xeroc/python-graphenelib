.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 grapheneapi/ graphenebase/ grapheneextra/

#test:
#	py.test tests

#test-all:
#	tox
#

build:
	python3 setup.py build

install: build
	python3 setup.py install

install-user: build
	python3 setup.py install --user

release: clean
	python3 setup.py check
	python3 setup.py sdist upload -r pypi
	python3 setup.py bdist --format=wininst,zip upload

