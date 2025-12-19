# exported tasks:
# make prepare-all
# make build-wheel
# make package


.PHONY: prepare-all


# prepare a build environment, with packages needed to build or push build artifacts
prepare-all: prepare-components
	# --system-site-packages is needed to access the system pywebview package during the pyinstaller bundling
	python3 -m venv build_venv --system-site-packages
	./build_venv/bin/pip install -r build_requirements.txt




# packaging tasks:
# package: build untext.tar.gz
#   before packaging, components must be built first with make build-components


.PHONY: package package-python package-onefile _prepare-cython cython

_prepare-cython:
	cp -r src cython-build

cython_files := $(shell cat cython-compile.list)
cython_files := $(addprefix cython-build/,$(cython_files))

cython_output := $(cython_files:.py=.so)


# python adds an ABI tag to the name of every cython .so file
# example:
# cythonize -i lib.py
# -> lib.cpython-313-x86_64-linux-gnu.so
# renaming to lib.so does not break imports
%.so: %.py
	./build_venv/bin/cythonize -i $< -3
	mv $(basename $<).*.so $(basename $<).so
	rm $(basename $<).py


cython: _prepare-cython $(cython_output)
	# remove trash:
	# cython c files
	find cython-build/untext/ -name "*.c" -delete
	# cython build/ directories
	find cython-build -type d -name build -exec rm -rf {} +
	# __pycache__/ directories
	find cython-build/ -name __pycache__ -exec rm -rf {} +
	# pip package entrypoint (python3 -m untext), not used with the pyinstaller+cython builds
	rm cython-build/untext/__main__.py



package: cython
	./build_venv/bin/pyinstaller cython-build/main.py --add-data cython-build/untext/css/:untext/css --add-data cython-build/untext/css/:untext/css
	mv dist/main dist/untext
	mv dist/untext/main dist/untext/untext
	cd dist && tar -czf untext.tar.gz untext
	mv dist/untext ./untext
	mv dist/untext.tar.gz ./
	rm -r build






.PHONY: prepare-components build-components

prepare-components:
	cd custom-elements && npm i

build-components:
	cd custom-elements && npm run build
	cp custom-elements/dist/assets/*.js src/untext/js/components.js
	cp custom-elements/dist/assets/*.css src/untext/css/components.css






# wheel tasks:
# build-wheel: build a new wheel in dist/ (with the version number set in pyproject.toml)


.PHONY: build-wheel


# build a wheel (.whl) and an sdist (source dist, .tar.gz) in ./dist/
# components must be built first, with build-components
build-wheel:
	./build_venv/bin/python -m build

