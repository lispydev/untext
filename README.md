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

You can then clone the repository and run untext directly:
```sh
git clone https://github.com/lispydev/untext
cd untext/src
python3 main.py
```

At the time of writing, starting untext will simply parse its own code and render it as html, with one window per file. The keybindings "r" and "s" are defined to run/reload the current file and spawn a python shell in the same module.


To run untext with pywebview installed in a virtual environment, you will need to build pywebview. You can find more information in [pypy.md](pypy.md), as well as instructions to run untext on pypy (Both CPython 3.13 and Pypy 3.11 are supported).

