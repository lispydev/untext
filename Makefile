# makefile for development
#
#
# If this is your first time using this repository, just run `make`.
# This will setup everything to get you started.
#
# Then, you can use:
# make update-components: rebuild submodule dependencies (use after editing the custom-elements submodule)
# make dev: quickly build untext in ./untext
# make wheel: build a pip release in dist/
#
# to build a new release:
# edit pyproject.toml to bump the version
# make release: build untext(.tar.gz) and pip releases in dist/
# make test-wheel: create a test venv with the latest pip release found in dist/
# make push-wheel: upload to PyPI (needs a pypi account)
#


.PHONY: default prepare update-components dev wheel release test-wheel push-wheel


#######

# for first-users
default: prepare update-components release


# run once after cloning the repository
prepare:
	# prepare submodules
	cd custom-elements && npm i
	rm -rf build_venv
	# --system-site-packages leaves the pywebview setup to the user
	python3 -m venv build_venv --system-site-packages
	./build_venv/bin/pip install -r build_requirements.txt

# run after editing web components
update-components:
	cd custom-elements && npm run build
	cp custom-elements/dist/assets/*.js src/untext/js/components.js
	cp custom-elements/dist/assets/*.css src/untext/css/components.css

# package quickly without compiling with cython
# it is even faster to run directly with python3 -m untext
dev:
	rm -rf untext  # force clean builds
	./build_venv/bin/pyinstaller src/main.py --add-data src/untext/css/:untext/css --add-data src/untext/js/:untext/js
	rm -r build
	mv dist/main ./untext
	mv untext/main untext/untext

wheel:
	rm -rf dist/*
	./build_venv/bin/python -m build


release:
	rm -rf untext
	rm -rf dist/*
	docker build . -f docker/Dockerfile --output type=local,dest=./


# pip releases

# make a venv with the latest built wheel installed
test-wheel:
	rm -rf test_venv
	python3 -m venv --system-site-packages test_venv
	./test_venv/bin/pip install pywebview
	$(eval last_build := $(shell find dist | tail -n 1))
	./test_venv/bin/pip install $(last_build)
	@echo "Created a test_venv with $(last_build) ."
	@echo "Untext is installed in the test_venv virtual environment."
	@echo "You will not be able to run it unless you have a working pywebview set up."
	@echo "You can test pywebview with ./test_venv/bin/python -m untext.webview_test"



# push the wheel to pypi.org
push-wheel:
	# pushing dist/untext-*.whl and dist/untext-*.tar.gz to PyPI
	# the build artifacts are built with the `make release` command
	./build_venv/bin/python -m twine upload --repository testpypi dist/*
	./build_venv/bin/python -m twine upload --repository pypi dist/*



#clean:
#	# cache files in src
#	find src -name __pycache__ -exec rm -rf {} +


