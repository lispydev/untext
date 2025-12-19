# wheel tasks:
# build-wheel: build a new wheel in dist/ (with the version number set in pyproject.toml)
# push: upload to pypi.org
#
# test tasks:
# testpush: upload to test.pypi.org
# test-wheel-local: make a venv (test-venv) from the latest wheel in dist/
#
#
# cleanup tasks:
# clean-tests: remove test_venv



.PHONY: build-wheel push testpush test-wheel-local clean-tests _setup-test-venv


# build a wheel (.whl) and an sdist (source dist, .tar.gz) in ./dist/
# components must be built first, with build-components
build-wheel:
	./build_venv/bin/python -m build
	

# push the wheel to pypi.org
push:
	./build_venv/bin/python -m twine upload --repository pypi dist/*

# push the wheel to test.pypi.org
testpush:
	./build_venv/bin/python -m twine upload --repository testpypi dist/*


# wheel test tasks


# make a venv with the latest built wheel installed
test-wheel-local: clean-tests _setup-test-venv
	$(eval last_build := $(shell find dist | tail -n 1))
	./test_venv/bin/pip install $(last_build)
	@echo "Created a test_venv with $(last_build) ."
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"


_setup-test-venv:
	@# the system-wide pywebview must be used if it is available,
	@# because pywebview cannot be pip installed without platform-specific libraries for GTK/Qt
	python3 -m venv --system-site-packages test_venv
	./test_venv/bin/pip install pywebview



clean-tests:
	rm -rf test_venv



.PHONY: _test-wheel-test _test-wheel-prod


# these test tasks were useful during the initial packaging setup, but are not really used anymore since test-wheel-local gives the same behavior

# same as test-wheel-local, but download the wheel from test.pypi.org
_test-wheel-test: clean-tests _setup-test-venv
	#./test_venv/bin/pip install --index-url https://test.pypi.org/simple --no-deps untext
	./test_venv/bin/pip install --index-url https://test.pypi.org/simple untext
	#./test_venv/bin/pip install untext
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"


# test the actual pip install
_test-wheel-prod: clean-tests _setup-test-venv
	./test_venv/bin/pip install untext
#	./test_venv/bin/pip install --index-url https://test.pypi.org/simple untext
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"




