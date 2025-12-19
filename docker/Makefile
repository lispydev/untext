# exported tasks:
# make prepare-all
# make build-wheel
# make package


include packaging.mk
include wheel.mk
include components.mk

.PHONY: prepare-all


# prepare a build environment, with packages needed to build or push build artifacts
prepare-all: prepare-components
	# --system-site-packages is needed to access the system pywebview package during the pyinstaller bundling
	python3 -m venv build_venv --system-site-packages
	./build_venv/bin/pip install -r build_requirements.txt

