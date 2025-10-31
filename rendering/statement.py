"""
statement rendering
"""

# types
from webview.dom.dom import DOM
from webview.dom.element import Element
import ast

from .dom import register, div, block
from . import expression


def render(dom: DOM, parent: Element, node: ast.stmt):
    match type(node):
        case ast.FunctionDef:
            render_funcdef(dom, parent, node)
        case ast.AsyncFunctionDef:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncFunctionDef")
        case ast.ClassDef:
            raise NotImplementedError("statement.render() not implemented for ast.ClassDef")
        case ast.Return:
            raise NotImplementedError("statement.render() not implemented for ast.Return")

        case ast.Delete:
            raise NotImplementedError("statement.render() not implemented for ast.Delete")
        case ast.Assign:
            raise NotImplementedError("statement.render() not implemented for ast.Assign")
        case ast.TypeAlias:
            raise NotImplementedError("statement.render() not implemented for ast.TypeAlias")
        case ast.AugAssign:
            raise NotImplementedError("statement.render() not implemented for ast.AugAssign")
        case ast.AnnAssign:
            raise NotImplementedError("statement.render() not implemented for ast.AnnAssign")

        case ast.For:
            raise NotImplementedError("statement.render() not implemented for ast.For")
        case ast.AsyncFor:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncFor")
        case ast.While:
            raise NotImplementedError("statement.render() not implemented for ast.While")
        case ast.If:
            raise NotImplementedError("statement.render() not implemented for ast.If")
        case ast.With:
            raise NotImplementedError("statement.render() not implemented for ast.With")
        case ast.AsyncWith:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncWith")

        case ast.Match:
            raise NotImplementedError("statement.render() not implemented for ast.Match")

        case ast.Raise:
            raise NotImplementedError("statement.render() not implemented for ast.Raise")
        case ast.Try:
            raise NotImplementedError("statement.render() not implemented for ast.Try")
        case ast.TryStar:
            raise NotImplementedError("statement.render() not implemented for ast.TryStar")
        case ast.Assert:
            raise NotImplementedError("statement.render() not implemented for ast.Assert")

        case ast.Import:
            render_import(dom, parent, node)
        case ast.ImportFrom:
            render_importfrom(dom, parent, node)

        case ast.Global:
            raise NotImplementedError("statement.render() not implemented for ast.Global")
        case ast.Nonlocal:
            raise NotImplementedError("statement.render() not implemented for ast.Nonlocal")
        case ast.Expr:
            pass
            #raise NotImplementedError("statement.render() not implemented for ast.Expr")
        case ast.Pass:
            raise NotImplementedError("statement.render() not implemented for ast.Pass")
        case ast.Break:
            raise NotImplementedError("statement.render() not implemented for ast.Break")
        case ast.Continue:
            raise NotImplementedError("statement.render() not implemented for ast.Continue")

        case default:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")


            #if isinstance(node, ast.Import):
            #    return render_import(node)
            #elif isinstance(node, ast.ImportFrom):
            #    return render_importfrom(node)
            #elif isinstance(node, ast.FunctionDef):
            #    return render_funcdef(node)
            #elif isinstance(node, ast.Expr):
            #    return render_expr_statement(node)
            #elif isinstance(node, ast.With):
            #    return render_with(node)
            #elif isinstance(node, ast.Assign):
            #    return render_assign(node)
            #elif isinstance(node, ast.While):
            #    return render_while(node)
            #elif isinstance(node, ast.For):
            #    return render_for(node)
            #elif isinstance(node, ast.Assert):
            #    return render_assert(node)
            #elif isinstance(node, ast.Return):
            #    return render_return(node)
            #elif isinstance(node, ast.If):
            #    return render_if(node)
            #elif isinstance(node, ast.Pass):
            #    return render_pass(node)
            #elif isinstance(node, ast.Try):
            #    return render_try(node)
            #elif isinstance(node, ast.Raise):
            #    return render_raise(node)
            #elif isinstance(node, ast.AugAssign):
            #    targ = render_expr(node.target)
            #    op = render_binaryop(node.op)
            #    val = render_expr(node.value)
            #    return f"{targ} {op}= {val}"
            #else:
            #    raise NotImplementedError(type(node))



# TODO: find a place to put this function (main.py ?)
# modules are not statements, they are top-level programs
def render_module(dom, parent, node):
    elt = dom.create_element(div(), parent=parent)
    print(type(elt))
    register(node, elt)
    for stmt in node.body:
        render(dom, elt, stmt)
    print(node.id)
    print(elt)
    print(node)


"""
AST statement node rendering
"""

def render_import(dom: DOM, parent: Element, node: ast.Import):
    elt = dom.create_element(div(), parent=parent)
    register(node, elt)
    elt.classes = ["import", "row"]
    text = dom.create_element(div(), elt)
    text.text = "import "
    for name in node.names:
        render_alias(dom, elt, name)

# sub-part of import and importfrom nodes
def render_alias(dom: DOM, parent: Element, node: ast.alias):
    text = dom.create_element(div(), parent=parent)
    if node.asname is not None:
        # TODO: use sub-nodes to encode semantically ?
        text.text = f"{node.name} as {node.asname}"
    else:
        text.text = f"{node.name}"


def render_importfrom(dom: DOM, parent: Element, node: ast.ImportFrom):
    assert node.level == 0
    elt = dom.create_element(div(), parent=parent)
    register(node, elt)
    elt.classes = ["importfrom", "row"]
    text1 = dom.create_element(div(), elt)
    text1.text = "from"
    text2 = dom.create_element(div(), elt)
    text2.text = node.module
    text3 = dom.create_element(div(), elt)
    text3.text = "import"
    fragments_div = dom.create_element(div(), elt)
    fragments_div.classes = ["row"]
    for name in node.names:
        render_alias(dom, fragments_div, name)


def render_funcdef(dom: DOM, parent: Element, node: ast.FunctionDef):
    assert len(node.type_params) == 0
    elt = dom.create_element(div(), parent=parent)
    register(node, elt)
    elt.classes = ["funcdef"]
    header = dom.create_element(div(), parent=elt)
    header.classes = ["header", "row-nogap", "block-header"]
    funcname = dom.create_element(div(), header)
    funcname.classes = ["name", "row-nogap", "gap", "def-prefix"]
    funcname.text = node.name
    params = dom.create_element(div(), header)
    params.classes = ["parens", "row-nogap"]
    params_content = dom.create_element(div(), params)
    params_content.classes = ["comma-sep", "row-nogap"]
    render_parameters(dom, params_content, node.args)
    return

    n = node
    body = []
    header = f"def {n.name}({render_arguments(n.args)}):"
    for statement in n.body:
        body.append(render_statement(statement))
    # TODO: support decorators in function definitions
    assert len(n.decorator_list) == 0
    # never seen otherwise yet
    assert n.returns is None
    assert n.type_comment is None

    header = div(header)
    body = "".join(body)
    body = block(body)
    return div(header + body)

# sub-part of render_funcdef
def render_parameters(dom: DOM, parent: Element, node: ast.arguments):
    # TODO: support more cases
    assert len(node.posonlyargs) == 0
    assert len(node.kwonlyargs) == 0
    assert len(node.kw_defaults) == 0
    assert len(node.defaults) == 0
    # flags (*args and **kwargs)
    assert node.vararg is None
    assert node.kwarg is None
    for param in node.args:
        render_param(dom, parent, param)
    #result = ", ".join([render_arg(arg) for arg in node.args])
    #return result

# sub-part of render_parameters
def render_param(dom: DOM, parent: Element, node: ast.arg):
    # TODO: support argument type annotations
    assert node.annotation is None
    assert node.type_comment is None
    # text metadata (not needed in a no-text IDE)
    #print(arg.lineno)
    #print(arg.col_offset)
    #print(arg.end_lineno)
    #print(arg.end_col_offset)
    elt = dom.create_element(div(), parent=parent)
    elt.text = node.arg
