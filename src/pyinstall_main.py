"""
main entrypoint when built with pyinstaller
"""

#equivalent arguments in the pyinstaller build step: --hidden-import pywebview --hidden-import webview --hidden-import code --hidden-import untext.rendering.dynamic.statement --hidden-import untext.rendering.dynamic.expression --hidden-import untext.rendering.static --onefile

import webview
import webview
import code
import untext.rendering.dynamic.statement
import untext.rendering.dynamic.expression
import untext.rendering.static


# TODO: remove
# (the pyinstaller build step would strip the current directory from sys.path)
#import sys
#sys.path.insert(0, ".")
from untext.main import main

main()
