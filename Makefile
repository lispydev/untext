.PHONY: build_prepare build push testpush test_wheel_local test_wheel test_wheel_prod clean-tests cython pyinstall clean-cython


#####


# pip packaging tasks


# prepare a build environment
# build: builds wheel and sdist output
# twine: upload to pypi
# mypy (and system packages): static analysis
build_prepare:
	python3 -m venv build_venv --system-site-packages
	./build_venv/bin/pip install -r build_requirements.txt

# build a wheel (.whl) and an sdist (source dist, .tar.gz) in ./dist/
build:
	./build_venv/bin/python -m build

# push the wheel to pypi.org
push:
	./build_venv/bin/python -m twine upload --repository pypi dist/*

# push the wheel to test.pypi.org
testpush:
	./build_venv/bin/python -m twine upload --repository testpypi dist/*


####

# wheel test tasks


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




#######


# cython/pyinstaller packaging tasks

# not used anymore; was used before finalizing the pyinstaller+cython build process
pyinstall_python:
	# multi-file build is faster to start, when testing
	#./build_venv/bin/pyinstaller src/pyinstall_main.py --add-data src/untext/css/:untext/css
	./build_venv/bin/pyinstaller src/pyinstall_main.py --add-data src/untext/css/:untext/css --onefile
	# cleanup
	rm -r build
	mv dist/pyinstall_main ./untext


prepare_cython:
	cp -r src/ src-cython


src := rendering/dynamic/statement.py \
       rendering/dynamic/dom.py \
       rendering/dynamic/expression.py \
       rendering/static/expression.py \
       rendering/static/html.py \
       rendering/static/statement.py \
       main.py


# test mode; try without the files that cannot currently be compiled by cython
src := rendering/dynamic/dom.py \
       rendering/static/html.py \
       main.py


src := $(addprefix src-cython/untext/, $(src))

so := $(src:.py=.so)

src-cython/untext/%.so: src-cython/untext/%.py
	./build_venv/bin/cythonize -i $< #-3
	# python adds an ABI tag to the name of every cython .so file
	# example:
	# cythonize -i lib.py
	# -> lib.cpython-313-x86_64-linux-gnu.so
	# renaming to lib.so does not break imports
	mv $(basename $<).*.so $(basename $<).so

cython: prepare_cython $(so)
	find src-cython/untext/ -name "*.c" -delete
	# TODO: switch once all modules can compile with cython
	# find src-cython/untext/ -name "*.py" -delete
	rm src-cython/untext/rendering/dynamic/dom.py
	rm src-cython/untext/rendering/static/html.py
	rm src-cython/untext/main.py

clean-cython:
	rm -r src-cython


package: clean-cython cython
	# note: 
	# --hidden-import <import path> can be used to add the dependencies that pyinstaller cannot see inside cython files
	# the imports can also be added in src/pyinstall_main.py to expose them to pyinstaller; so long as this file itself is not compiled with cython
	# note:
	# building without --onefile is faster and gives much faster boot times
	# building with --onefile gives properly packaged binaries
	# for the end user, having faster start times is preferable to having a single file
	./build_venv/bin/pyinstaller src-cython/pyinstall_main.py --add-data src-cython/untext/css/:untext/css #--onefile
	# single file:
	#mv dist/pyinstall_main ./untext
	# multi file:
	mv dist/pyinstall_main untext
	tar -cvfz untext.tar.gz untext




