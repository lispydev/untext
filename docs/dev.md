# Developing Untext

In order to edit the source code and build your own version of untext, you will need:
- `make`, to build pip releases and push to PyPI repositories
- docker or equivalent, to build a portable app

The windows installation is not fully documented yet, because the containerized build is still a work in progress.

## Linux

### Setup

Start by cloning the repository and running make once to initialize everything and build a release:
```
git clone https://github.com/lispydev/untext
cd untext
make
```


### Development

Before building anything, you can test your code by running Untext with Python. You will need Pywebview installed to do this:
```sh
cd src
python3 src/main.py src/untext/main.py
```
Since this will create temporary `__pycache__` files which should not be bundled into the release, you must run this to cleanup the source directory before building something:
```sh
find ./src/ -name __pycache__ -exec rm -r {} +
```
Or simply `make clean-cache`.


Instead, you can also build a pure python portable app with:
```sh
make dev
```
This will create the `untext` directory in the repository, which contains everything needed for:
```sh
./untext/untext src/untext/main.py
```
Note:
This bundle is unsuitable for production releases, because PyInstaller will bundle personal files (such as your gtk themes) along with the dependencies.
The correct way to build for release is explained below, and uses a container to make sure the build output is independant from the machine used for building.



### Building a Pip release

The pip release is built when making a full release with `make release`.
You can also make just the pip package with `make wheel`.

The build artifacts will be in `dist/`.
You can test the pip package with `make test-wheel`. This will create a venv in `test_venv`, which will have pywebview and the untext wheel pre-installed.
You can then run untext with:
```sh
./test_venv/bin/python -m untext src/untext/main.py
```


If you have a PyPI.org account with an access token configured, you can publish the release with `make push-wheel`. Be careful when publishing a package, versions cannot be altered after pushing to PyPI (even by deleting them from PyPI).


### Building a portable release

Simply run `make release`.
You will need docker for this task to run.
This will build the app in the `untext` directory, and compress it in `untext.tar.gz` (the build artifact on github).


This will output:
- `./untext` and `./untext.tar.gz`: the portable build for Linux
- `dist/untext-<version>-none-any.whl` and `dist/untext-<version>.tar.gz`: the pip releases for sharing on pypi and installing with pip



## Windows

Windows is exclusively used for building portable windows apps. Development and pip builds are done on Linux.

### Building a portable release
TODO


