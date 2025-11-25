# Untext

Untext is a textless Python *interactive* development environment built in Python.

Unlike other IDEs, untext does not include a text editor, and goes straigth to the AST layer for syntax-aware editing capabilities.

Untext uses a webview to render the UI from Python, with css to bridge the gap between AST attributes and readable code on the screen.


# How to run

Untext is still in development.

To try it now, you need the [pywebview](https://pywebview.flowrl.com/) library installed.

On debian, you can install all the dependencies with:
```sh
apt install python3-webview
```


You can then install untext with pip:
```sh
pip install untext
# open script.py with untext
python3 -m untext ./script.py
```

If you want to install untext in a virtual environment, it is recommended that you use the pywebview installed by your distro package manager (on Linux, pip install pywebview will result in a pywebview install with no GUI backend):
```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install untext
```

To run untext with pywebview installed in a virtual environment, you will need to build pywebview. You can find more information and an example for the GTK backend in [pypy.md](pypy.md), as well as instructions to run untext on pypy (Both CPython 3.13 and Pypy 3.11 are supported).




For development, you can test untext locally by cloning the repository, as long as you have pywebview installed:
```sh
git clone https://github.com/lispydev/untext
cd untext/src
python3 -m untext
```



## Status
At the time of writing, untext can only render existing Python code. The keybindings "r" and "s" are defined to run/reload the current file and spawn a python shell in the same module.


