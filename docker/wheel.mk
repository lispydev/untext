# wheel tasks:
# build-wheel: build a new wheel in dist/ (with the version number set in pyproject.toml)


.PHONY: build-wheel


# build a wheel (.whl) and an sdist (source dist, .tar.gz) in ./dist/
# components must be built first, with build-components
build-wheel:
	./build_venv/bin/python -m build
	
