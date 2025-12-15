# packaging tasks:
# package: build untext.tar.gz
#
# tasks used when testing:
# package-onefile: build as a single file binary (more convenient when testing portability, but lower boot times)
# package-python: pure python build, without compiling with cython (faster to build when testing)
#
# cleanup tasks (called automatically):
# _clean-cython
# _clean-package


.PHONY: package package-python package-onefile _clean-package _prepare-cython _clean-cython cython


# not used anymore; can still be used for quick tests
package-python: #build_components
	# multi-file build is faster to start and faster to build, when testing
	./build_venv/bin/pyinstaller src/pyinstall_main.py --add-data src/untext/css/:untext/css --add-data src/untext/js/:untext/js
	# cleanup
	rm -r build
	mv dist/pyinstall_main ./untext

_prepare-cython:
	cp -r src cython-build
_clean-cython:
	rm -rf cython-build

cython_files := $(shell cat cython-compile.list)
cython_files := $(addprefix cython-build/,$(cython_files))

cython_output := $(cython_files:.py=.so)


# python adds an ABI tag to the name of every cython .so file
# example:
# cythonize -i lib.py
# -> lib.cpython-313-x86_64-linux-gnu.so
# renaming to lib.so does not break imports
%.so: %.py
	./build_venv/bin/cythonize -i $< #-3
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


_clean-package:
	rm -f untext.tar.gz
	rm -rf untext


# not bundling to a single file gives faster boot times
package: _clean-cython _clean-package cython #build_components
	./build_venv/bin/pyinstaller cython-build/pyinstall_main.py --add-data cython-build/untext/css/:untext/css --add-data cython-build/untext/css/:untext/css
	# some files are bundled by pyinstaller without being actually needed
	# TODO: build in a docker container without the bloat of my personal computer
	rm -r dist/pyinstall_main/_internal/share
	mv dist/pyinstall_main dist/untext
	mv dist/untext/pyinstall_main dist/untext/untext
	cd dist && tar -czf untext.tar.gz untext
	mv dist/untext.tar.gz ./
	rm -r dist/untext
	rm -r build

# used for testing (single files are easier to move around)
package_onefile: _clean-cython _clean-package cython #build_components
	./build_venv/bin/pyinstaller cython-build/pyinstall_main.py --add-data cython-build/untext/css/:untext/css --add-data cython-build/untext/js/:untext/js --onefile
	mv dist/pyinstall_main ./untext
	rm -r build

