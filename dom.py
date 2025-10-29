# use unique ids to link python AST nodes to webview Element nodes
dom_mapping = {}
ast_mapping = {}

def make_counter():
    counter = 0
    def count():
        nonlocal counter
        counter += 1
        return counter

genid = make_counter()

"""
basic wrappers over html string formatting
"""

def div(html):
    return f"<div>{html}</div>"

def block(html):
    return f"<div class='block'>{html}</div>"


def render_if(if_node):
    pass
