# Advanced installation methods

While untext itself is a pure python project, it relies on [pywebview](https://pywebview.flowrl.com/), which is installed in many different ways:
- by installing a package from your distribution
- by building and providing headers for a GUI backend (Gtk or Qt)

The simplest way to install Untext is to simply [download a release](https://github.com/lispydev/untext/releases/). These releases are compiled with Cython and contain all the dependencies needed, so they should.

Pywebview itself also has a documentation on how to install it, and most Linux distributions should have a package to install pywebview without dealing with build dependencies.

This documentation is for users with special needs. These examples should cover most use cases.


## Checking if an installation work

If you want to make sure pywebview is properly installed, you can run:
If you get errors related to pywebview, you can check that pywebview is working properly by running:
```sh
python3 -m untext.webview_test
```
If the pywebview website opens in a window, pywebview is working properly and untext will work too.

If you receive errors about GTK or Qt, this means Pywebview is missing a rendering backend.
The main thing that can cause this error is installing pywebview with pip without specifying a GUI backend:
```sh
pip install pywebview  # wrong
pip install pywebview[gtk]  # will compile with GTK headers
pip install pywebview[qt]  # will compile for Qt
```


## Running in a venv with the distribution-managed pywebview

The easiest way to install pywebview is by installing a global package. If you do not wish to install untext globally, you can use a venv that has access to system packages:
```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install untext
```


## Running the latest untext commit

Note:
Using the latest commit on github is not recommended, because the code may contain bugs which are not fixed or does not match the documentation.

If you still want to get the latest code, you can test untext locally by cloning the repository, as long as you have pywebview installed:
```sh
git clone https://github.com/lispydev/untext
cd untext/src
python3 -m untext
```

In order to use untext everywhere in your system, you must build a wheel and pip install it. The instructions to do so are in the [development documentation](docs/dev.md).



## Running with Pypy and the latest Pywebview in a venv

During development, untext is usually tested with both the Debian `python3-webview` package and the latest pip release, so there should not be any version incompatibility issue from using a different pywebview version.

Nevertheless, if you want to run untext with the latest pywebview release, or if you just want to run untext with pypy, you can do so by installing pywebview in a venv with pip.

Building pywebview with Qt is not covered because I do not use Qt.
These build instructions are tested on Debian 13 Trixie.


### Python version concerns

At the time of writing, Pypy is still in Python 3.11, while CPython is in 3.13.

Due to the hard dependency on the specific AST structure, untext cannot use the 3.12+ FunctionDef `type_params` attribute for type annotations and run under Pypy.

Untext can run with Pypy 3.11, but will stop supporting 3.11 as soon as Pypy updates to 3.12, in order to have access to more AST information.

### Dependencies

Untext uses `pywebview` for its GUI, which depends on a native GUI library (GTK, Qt,...).

While these native dependencies are sorted automatically when pywebview is packaged by the distro, pywebview is usually only packaged for CPython.

To run untext with pypy, you will need to build packages with pip, native library headers (GTK is used here) and pypy headers instead of CPython ones.

On Debian, you can run untext with pypy using GTK using a virtual environment and these dependencies:
```sh
apt install pypy3-venv pypy3-dev libcairo2-dev libgirepository-2.0-dev
```

To prepare the environment:
```sh
pypy3 -m venv _venv
_venv/bin/pip install pycairo
_venv/bin/pip install git+https://gitlab.gnome.org/GNOME/pygobject.git
_venv/bin/pip install pywebview
```

You can check that pywebview is working by running `src/webview_test.py`:
```sh
_venv/bin/python src/webview_test.py
```
If pywebview is installed correctly, you should see the pywebview documentation open in a window.


You can then run untext with:
```sh
_venv/bin/pypy src/main.py
```


