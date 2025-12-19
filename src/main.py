"""
main entrypoint when built with pyinstaller
"""

#import sys
#sys.path.insert(0, ".")


#equivalent arguments in the pyinstaller build step: --hidden-import pywebview --hidden-import webview --hidden-import code --hidden-import untext.rendering.dynamic.statement --hidden-import untext.rendering.dynamic.expression --hidden-import untext.rendering.static --onefile

import webview
import webview
import code
import untext.rendering.dynamic
import untext.rendering.static


from untext.main import main

main()
