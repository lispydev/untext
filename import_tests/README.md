# Import and hot reload test suite

This directory contains manual tests for dynamic module execution and hot module reload.

While waiting for automated tests, this test suite can be used to verify that imports work without regressions, or debug existing bugs.


## How to use

To test a specific version of untext, simply start untext in this directory and open all the python files:
```sh
python3 -m untext $(find . -type f | grep -v "\.pyc" | grep -v README.md)
```

This will open a window for each python file (beware the number of opened windows, 9 at the time of writing). Every module can be reloaded by pressing "r" on its window, and a shell can be spawned inside the module by pressing "s".


To test a currently checked out version of untext, you can build the wheel and setup a test venv with these commands at the root of this repository:
```sh
make build
make test_wheel_local
cd import_tests
../test_venv/bin/python -m untext $(find . -type f | grep -v "\.pyc" | grep -v README.md)
```


## What is tested

- relative imports
- absolute (local) imports
- finding modules inside packages
- importing packages with a `__init__.py` file and namespace packages without a `__init__.py` file
- running `__init__.py` files
- repeated imports of a cached module (tested by mutating values inside the module)

Due to the manual nature of the tests, the one testing must make sure to test exhaustively, with different load orders (some modules may be known by python but not by the IDE, or the opposite, when something is buggy)

