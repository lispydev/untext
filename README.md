# Untext

Untext is a textless Python interactive development environment built in Python.

Unlike other IDEs, untext does not include a text editor, and goes straight to the AST layer for syntax-aware editing capabilities.

Untext uses a webview to render the UI from Python, with css to bridge the gap between AST nodes and readable code on the screen, and Web Components for interactivity.


## Status

At the time of writing, untext can only render existing Python code. The keybindings "r" and "s" are defined to run/reload the current file and spawn a python shell in the same module.


To be more specific, untext has:
- a Python AST -> HTML renderer, with a bidirectional AST <-> DOM mapping
- css-based syntax rendering
- cython compilation
- cross-platform, portable build process (Windows and Linux)
- live REPL injection inside your Python modules
- live module reload while your code is running
- pip packaging
- svelte/tailwind-based web components for the frontend
- containerized build on linux

The next steps are:
- containerized build on windows
- writing web components for the UI
- code edition commands
- keybindings
- python integrations
- project management GUI
- using Untext to write software


# How to run

Untext can be downloaded in the [github releases](https://github.com/lispydev/untext/releases) for Windows and Linux (tested on Debian 13).
Add the untext directory to your path so that you can run `untext main.py` from anywhere in your system.
This is the recommended installation process, with no dependency management and with Cython-compiled code.




You can also install untext with pip, but you will need the [pywebview](https://pywebview.flowrl.com/guide/installation.html) python package installed:
```sh
apt install python3-webview
pip install untext
```
You can then run untext with python from anywhere in your system:
```sh
python3 -m untext ./script.py
```

For other configurations and for troubleshooting the installation with pip, see the [advanced installation methods](docs/install.md) documentation.


# How to build

If you want to edit and build untext yourself, see the [development documentation](docs/dev.md).

