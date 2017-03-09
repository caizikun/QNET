PROJECT_NAME = QNET
PACKAGES =  pip numpy matplotlib scipy sympy ipython bokeh pytest sphinx nose ply cython coverage
TESTPYPI = https://testpypi.python.org/pypi

#TESTOPTIONS = --doctest-modules --cov=qnet
TESTOPTIONS = --doctest-modules --cov=qnet
TESTS = qnet tests
# You may redefine TESTS to run a specific test. E.g.
#     make test TESTS="tests/algebra"

VERSION = $(shell grep __version__ < qnet/__init__.py | sed 's/.*"\(.*\)"/\1/')

DOC = qnet-doc-$(VERSION)

develop:
	pip install --process-dependency-links -e .[simulation,circuit_visualization,dev]

install:
	pip install --process-dependency-links .

uninstall:
	pip uninstall $(PROJECT_NAME)

sdist:
	python setup.py sdist

upload:
	python setup.py register
	python setup.py sdist upload

test-upload:
	python setup.py register -r $(TESTPYPI)
	python setup.py sdist upload -r $(TESTPYPI)

test-install:
	pip install -i $(TESTPYPI) $(PROJECT_NAME)

clean:
	@rm -rf build
	@rm -rf dist
	@rm -rf QNET.egg-info
	@find . -iname *pyc | xargs rm -f
	@find . -iname __pycache__ | xargs rm -rf
	@make -C docs clean
	@rm -rf $(DOC) $(DOC).tgz
	@rm -rf htmlcov
	@rm -rf .cache
	@rm -f .coverage

distclean: clean
	@rm -rf .venv

.venv/py35/bin/py.test:
	@conda create -y -c conda-forge -m -p .venv/py35 python=3.5 $(PACKAGES) qutip
	@.venv/py35/bin/pip install --process-dependency-links -e .[simulation,circuit_visualization,dev]

test35: .venv/py35/bin/py.test
	$< -v $(TESTOPTIONS) $(TESTS)

test: test35

coverage: test35
	@rm -rf htmlcov/index.html
	.venv/py35/bin/coverage html

doc: .venv/py35/bin/py.test
	@rm -f docs/API/qnet.*
	$(MAKE) -C docs SPHINXBUILD=../.venv/py35/bin/sphinx-build html
	@rm -rf $(DOC)
	@cp -r docs/_build/html $(DOC)
	tar -c $(DOC) | gzip > $(DOC).tgz
	@rm -rf $(DOC)

.PHONY: install develop uninstall upload test-upload test-install sdist clean \
test test35 doc coverage distclean
