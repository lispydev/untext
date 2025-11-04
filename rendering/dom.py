"""
general DOM manipulation utilities
"""

from webview.dom.element import Element
from ast import AST

"""
(bidirectional) AST-DOM linking

AST nodes are linked to DOM elements with a shared unique id
"""


dom_mapping = {}
ast_mapping = {}

def make_counter():
    counter = 0
    def count():
        nonlocal counter
        counter += 1
        return counter
    return count

genid = make_counter()

def register(ast_node: AST, dom_element: Element):
    n = genid()
    dom_element.id = n
    # .id is used by some node types
    ast_node.node_id = n
    dom_mapping[n] = dom_element
    ast_mapping[n] = ast_node

"""
basic wrappers for html string formatting

In practice, with the new dynamic DOM renderer,
the html content is always empty (children are appended after creation)
"""

def div_old(html=""):
    return f"<div>{html}</div>"
def div():
    return "<div></div>"

def block(html=""):
    return f"<div class='block'>{html}</div>"

# TODO: add an easy wrapper for elt = dom.create_element(div, parent=parent); elt.classes = [...]; register(elt)
# wrappers for Element creation, AST node registering and html class setup
def add(parent: Element, cls: str | list = None, text: str = None):
    elt = parent.append(div())
    if cls:
        elt.classes = cls.split(" ") if isinstance(cls, str) else cls
    if text:
        elt.text = text
    return elt

# TODO: deprecated, use add() instead
def add_text(parent: Element, text: str):
    elt = add(parent)
    elt.text = text
    return elt

def add_node(parent: Element, node: AST, cls: str | list = None, text: str = None):
    elt = add(parent, cls, text)
    register(node, elt)
    return elt

# TODO: find an API to add children with wrapping divs

#def add_managed_item(parent: Element, )
    #def comma_separated_list(parent: Element):
    #    elt = add(parent, "comma-sep")
    #    return elt
    #
    #def add_item(lst, *args)

#def add(parent, html):
#    parent.append(html)

#def row():
#    return "<div class='row'></div>"

