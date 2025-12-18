"""
main entrypoint when built with pyinstaller
"""

# in the container build process with a python3.13-slim image, python packages are not in the path
# this line forces imports to be resolvable so that pyinstaller bundles them
#import sys
#sys.path.append("/usr/lib/python3/dist-packages")
#sys.path.insert(0, ".")


#equivalent arguments in the pyinstaller build step: --hidden-import pywebview --hidden-import webview --hidden-import code --hidden-import untext.rendering.dynamic.statement --hidden-import untext.rendering.dynamic.expression --hidden-import untext.rendering.static --onefile

import webview
import webview
import code
import untext.rendering.dynamic.statement
import untext.rendering.dynamic.expression
import untext.rendering.static

# don't know who uses it, but something did
#import uuid
#import ssl # used by pywebview
#import socketserver


from untext.main import main

main()
