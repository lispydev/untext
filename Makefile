.PHONY: build push testpush testinstall_local testfetch clean-tests


# build a wheel (.whl) and an sdist (source dist, .tar.gz) in ./dist/
build:
	./build_venv/bin/python -m build

# push the wheel to pypi.org
push:
	./build_venv/bin/python -m twine upload --repository pypi dist/*

# push the wheel to test.pypi.org
testpush:
	./build_venv/bin/python -m twine upload --repository testpypi dist/*


# make a venv with the latest built wheel installed
test_wheel_local: clean-tests --setup_test_env
	$(eval last_build := $(shell find dist | tail -n 1))
	./test_venv/bin/pip install $(last_build)
	@echo "Created a test_venv with $(last_build) ."
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"


--setup_test_env:
	@# the system-wide pywebview must be used if it is available,
	@# because pywebview cannot be pip installed without platform-specific libraries for GTK/Qt
	python3 -m venv --system-site-packages test_venv
	./test_venv/bin/pip install pywebview



clean-tests:
	rm -rf test_venv



# these test tasks were useful during the initial packaging setup, but are not really used anymore since test_wheel_local gives the same behavior

# same as test_wheel_local, but download the wheel from test.pypi.org
test_wheel: clean-tests --setup_test_env
	#./test_venv/bin/pip install --index-url https://test.pypi.org/simple --no-deps untext
	./test_venv/bin/pip install --index-url https://test.pypi.org/simple untext
	#./test_venv/bin/pip install untext
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"

test_wheel_prod: clean-tests --setup_test_env
	./test_venv/bin/pip install untext
#	./test_venv/bin/pip install --index-url https://test.pypi.org/simple untext
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"
