# Running with Pypy and the latest Pywebview in a venv

This file documents how to pip install pywebview in a virtual environment (venv), and the steps to use pypy while doing so.

These steps are not used for development anymore, and the recommended way to use untext is with the portable releases.
This file is kept for archival and knownledge preservation, mostly on the subject of running the latest pywebview in a venv.


## Python version concerns

At the time of writing, Pypy is still in Python 3.11, while CPython is in 3.13.

Due to the hard dependency on the specific AST structure, untext cannot use the 3.12+ FunctionDef `type_params` attribute for type annotations and run under Pypy.

Untext can run with Pypy 3.11, but will stop supporting 3.11 as soon as Pypy updates to 3.12, in order to have access to more AST information.

## Dependencies

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


