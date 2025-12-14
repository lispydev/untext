# Untext

Untext is a textless Python interactive development environment built in Python.

Unlike other IDEs, untext does not include a text editor, and goes straight to the AST layer for syntax-aware editing capabilities.

Untext uses a webview to render the UI from Python, with css to bridge the gap between AST nodes and readable code on the screen, and Web Components for interactivity.


## Status

At the time of writing, untext can only render existing Python code. The keybindings "r" and "s" are defined to run/reload the current file and spawn a python shell in the same module.


# How to run

Untext can be downloaded in the [github releases](https://github.com/lispydev/untext/releases) for Windows and Linux (tested on Debian 13).
Add the untext directoryexecutable to your path so that you can run `untext main.py` from anywhere in your system.
This is the recommended installation process, with no dependency management and with Cython-compiled code.




You can also install untext with pip, but you will need the [pywebview](https://pywebview.flowrl.com/) python package installed:
```sh
apt install python3-webview  # alternatively, see: https://pywebview.flowrl.com/guide/installation.html
```
Then install untext:
```sh
pip install untext  # on debian, add --break-system-packages
```
You can then run untext with python from anywhere in your system:
```sh
python3 -m untext ./script.py
```

If something does not work, you can check that pywebview is working properly by running:
```sh
python3 -m untext.webview_test
```




If you want to install untext in a virtual environment, it is recommended that you use the pywebview installed by your distro package manager (on Linux, pip install pywebview will result in a pywebview install with no GUI backend):
```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install untext
```

To run untext with the latest pywebview installed in a virtual environment, you will need to build pywebview. You can find more information at [the pywebview install docs](https://pywebview.flowrl.com/guide/installation.html) or in the [running with pypy documentation](docs/dev/pypy.md), which uses venv to install pywebview.



For development, you can test untext locally by cloning the repository, as long as you have pywebview installed:
```sh
git clone https://github.com/lispydev/untext
cd untext/src
python3 -m untext
```



