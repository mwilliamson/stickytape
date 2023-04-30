.PHONY: test

test:
	sh -c '. _virtualenv/bin/activate; py.test tests'

.PHONY: upload

upload: test build-dist
	_virtualenv/bin/twine upload dist/*
	make clean

.PHONY: build-dist

build-dist: clean
	_virtualenv/bin/pyproject-build

.PHONY: clean

clean:
	rm -f MANIFEST
	rm -rf build dist

.PHONY: bootstrap

bootstrap: _virtualenv
	_virtualenv/bin/pip install -e .
ifneq ($(wildcard test-requirements.txt),)
	_virtualenv/bin/pip install -r test-requirements.txt
endif
	make clean

_virtualenv:
	python3 -m venv _virtualenv
	_virtualenv/bin/pip install --upgrade pip
	_virtualenv/bin/pip install --upgrade setuptools
	_virtualenv/bin/pip install --upgrade wheel
	_virtualenv/bin/pip install --upgrade build twine
