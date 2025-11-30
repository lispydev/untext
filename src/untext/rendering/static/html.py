"""
general HTML generation utilities
"""

# types
from ast import AST
from typing  import Tuple, Generator, List

HTMLGenerator = Generator[str, None, None] # yield str, receive None from send(), return None

HTML = Tuple[HTMLGenerator]
Classes = str | List[str]


# decorator for HTML generators
# usage:
# @debug
# def render_...
def debug(f):
    def g(node):
        for x in f(node):
            print(x)
            yield x
    return g




"""
(bidirectional) AST-DOM linking

AST nodes are linked to DOM elements with a shared unique id
"""
# TODO: centralize IDs
from untext.rendering.dynamic.dom import genid, register, ast_mapping

#def register(ast_node: AST, dom_element: Element):
#    n = genid()
#    dom_element.id = n
#    # .id is used by some node types
#    ast_node.node_id = n
#    dom_mapping[n] = dom_element
#    ast_mapping[n] = ast_node

"""
basic wrappers for html string formatting

HTML output is generated in ~O(n) where n is the size of the html code.
This is possible because of generators.
Expect lots of yield statements.
"""

# helpers
def id_attr(id) -> HTMLGenerator:
    # " id='{id}'"
    yield " id='"
    yield str(id)
    yield "'"

def class_attr(classes: Classes) -> HTMLGenerator:
    # " class='{...classes}'"
    yield " class='"
    if isinstance(classes, str):
        yield classes
    else:
        yield " ".join(classes)
    yield "'"


# main way of generating html
# we use a div soup because writing wrappers for every
# html tag adds complexity for no benefit
def div(*items: HTML, id=None, classes: Classes = []) -> HTMLGenerator:
    # <div {id} {class}>{items}</div>
    yield "<div"
    if id is not None:
        yield from id_attr(id)
    if classes:
        yield from class_attr(classes)
    yield ">"
    for x in items:
        yield from x
    yield "</div>"


def node(n: AST, *items: HTML) -> HTMLGenerator:
    id = genid()
    n.node_id = id
    # dom_mapping is useless because the Element does not exist yet and will have an id anyway
    ast_mapping[id] = n
    yield from div(*items, id=id)


# decorator for html renderers
def register_node(f):
    def renderer(n: AST):
        yield from node(n, f(n))
    return renderer


# usage: div(text("hello"))
def text(x: str) -> HTMLGenerator:
    yield x


# TODO: name
def element(classes: Classes, *items: HTML) -> HTMLGenerator:
    yield from div(classes=classes, *items)


# TODO: use for strings that contain spaces
# def pre():
#     return "<pre></pre>"
#
# def block(html=""):
#     return f"<div class='block'>{html}</div>"
#
# def add_pre(parent: Element, text: str):
#     elt = parent.append(pre())
#     elt.text = text
#     return elt

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


