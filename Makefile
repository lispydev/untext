# To build untext run:
# make prepare-all
# make build-all
# That's it.
#
# To build specific parts:
# make build-components (needed before building wheels and packaging)
# make build-wheel
# make package  # use this when packaging for the next release
# make package_onefile  # use this when testing build portability
# make package_python  # use this when iterating development (fastest to build)
#
# To publish a new release on pypi:
# edit pyproject.toml to bump the version
# make build-components
# make build-wheel
# make testpush
# make push
#
# To test the wheel after make build-wheel:
# make test-wheel-local
# ./test_venv/bin/python -m untext ./script.py
#
# clean commands (never needed):
# clean-tests: clean the test venv
# clean-all: clean all temporary files and packaged builds


include packaging.mk
include wheel.mk
include components.mk

.PHONY: prepare-all build-all clean-all default


#######

default: clean-all prepare-all build-all

# prepare a build environment, with packages needed to build or push build artifacts
prepare-all: prepare-components
	# --system-site-packages is needed to access the system pywebview package during the pyinstaller bundling
	python3 -m venv build_venv --system-site-packages
	./build_venv/bin/pip install -r build_requirements.txt


build-all: build-components build-wheel package

clean-all: _clean-cython _clean-package clean-tests
	# src cache files
	find src -name __pycache__ -exec rm -rf {} +
	# build_venv is kept
	#rm -rf build_venv

