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

def register(ast_node, dom_element):
    n = genid()
    dom_element.id = n
    ast_node.id = n
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
#def add(parent, html):
#    dom.create_element(html, parent=parent)

#def row():
#    return "<div class='row'></div>"

