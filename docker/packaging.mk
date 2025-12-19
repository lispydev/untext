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



# not bundling to a single file gives faster boot times
package: cython #build_components
	./build_venv/bin/pyinstaller cython-build/main.py --add-data cython-build/untext/css/:untext/css --add-data cython-build/untext/css/:untext/css
	mv dist/main dist/untext
	mv dist/untext/main dist/untext/untext
	cd dist && tar -czf untext.tar.gz untext
	mv dist/untext ./untext
	mv dist/untext.tar.gz ./
	rm -r build


