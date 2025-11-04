"""
statement rendering
"""

# types
from webview.dom.dom import DOM
from webview.dom.element import Element
import ast

from .dom import register, div, block, add_node, add, add_text
from . import expression


def render(parent: Element, node: ast.stmt):
    match type(node):
        case ast.FunctionDef:
            render_funcdef(parent, node)
        case ast.AsyncFunctionDef:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncFunctionDef")
        case ast.ClassDef:
            raise NotImplementedError("statement.render() not implemented for ast.ClassDef")
        case ast.Return:
            raise NotImplementedError("statement.render() not implemented for ast.Return")

        case ast.Delete:
            raise NotImplementedError("statement.render() not implemented for ast.Delete")
        case ast.Assign:
            render_assign(parent, node)
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
            return render_with(parent, node)
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
            render_import(parent, node)
        case ast.ImportFrom:
            render_importfrom(parent, node)

        case ast.Global:
            raise NotImplementedError("statement.render() not implemented for ast.Global")
        case ast.Nonlocal:
            raise NotImplementedError("statement.render() not implemented for ast.Nonlocal")
        case ast.Expr:
            expression.render(parent, node.value)
            #raise NotImplementedError("statement.render() not implemented for ast.Expr")
        case ast.Pass:
            render_pass(parent, node)
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
def render_module(parent: Element, node: ast.Module):
    elt = add_node(parent, node)
    for stmt in node.body:
        render(elt, stmt)


"""
AST statement node rendering
"""

def render_import(parent: Element, node: ast.Import):
    elt = add_node(parent, node, "import import-prefix row")
    aliases = add(elt, "aliases row comma-sep gap")
    for name in node.names:
        #comma_separated_item = add(aliases, "row")
        render_alias(aliases, name)

# sub-part of import and importfrom nodes
def render_alias(parent: Element, node: ast.alias):
    elt = add_node(parent, node, "alias row")
    if node.asname is not None:
        # create an alias (div (div name) "as" (div asname))
        alias = add(elt, "named-alias as-sep row")
        name = add_text(alias, node.name)
        asname = add_text(alias, node.asname)
    else:
        alias = add(elt, "unnamed-alias")
        name = add_text(alias, node.name)


def render_importfrom(parent: Element, node: ast.ImportFrom):
    assert node.level == 0
    elt = add_node(parent, node, "importfrom row gap")

    # prefixed items need .row and .gap to space their prefix and content
    from_prefixed = add(elt, "from-prefix row gap")
    from_field = add_text(from_prefixed, node.module)

    import_prefixed = add(elt, "import-prefix row gap")
    aliases = add(import_prefixed, "aliases row comma-sep gap")
    for name in node.names:
        render_alias(aliases, name)


def render_funcdef(parent: Element, node: ast.FunctionDef):
    assert len(node.type_params) == 0
    assert len(node.decorator_list) == 0
    # never seen otherwise yet
    assert node.returns is None
    assert node.type_comment is None
    elt = add_node(parent, node, "funcdef")
    header = add(elt, "row colon-suffix")
    funcname = add(header, "row gap def-prefix", node.name)
    params = add(header, "parens row")
    #params_content = add(params, "comma-sep row gap")
    render_parameters(params, node.args)
    body = add(elt, "block")

    for stmt in node.body:
        render(body, stmt)
    return

    n = node
    body = []
    for statement in n.body:
        body.append(render_statement(statement))
    # TODO: support decorators in function definitions

    header = div(header)
    body = "".join(body)
    body = block(body)
    return div(header + body)

# sub-part of render_funcdef
def render_parameters(parent: Element, node: ast.arguments):
    # TODO: support more cases
    assert len(node.posonlyargs) == 0
    assert len(node.kwonlyargs) == 0
    assert len(node.kw_defaults) == 0
    assert len(node.defaults) == 0
    # flags (*args and **kwargs)
    assert node.vararg is None
    assert node.kwarg is None
    elt = add(parent, "comma-sep row gap")
    for param in node.args:
        comma_separated_item = add(elt, "row")
        render_param(comma_separated_item, param)
    #result = ", ".join([render_arg(arg) for arg in node.args])
    #return result

# sub-part of render_parameters
def render_param(parent: Element, node: ast.arg):
    # TODO: support argument type annotations
    assert node.annotation is None
    assert node.type_comment is None
    # text metadata (not needed in a no-text IDE)
    #print(arg.lineno)
    #print(arg.col_offset)
    #print(arg.end_lineno)
    #print(arg.end_col_offset)

    # comma-separated items must be inlined,
    # so that the comma is on the same line
    elt = add_node(parent, node, "row", node.arg)


def render_with(parent: Element, node: ast.With):
    assert node.type_comment is None
    elt = add_node(parent, node)
    # this breaks if newlines are added for clarity:
    #header = elt.append("""<div class="with-prefix colon-suffix row gap"></div>""")
    header = add(elt, "with-prefix colon-suffix row gap")
    print(header)
    body = add(elt, "block")
    for item in node.items:
        render_withitem(header, item)
    return
    pass
    body = "".join([render_statement(statement) for statement in node.body])
    items = ", ".join([render_withitem(item) for item in node.items])
    header = div(f"with {items}:")
    body = block(body)
    result = div(header + body)
    return result


def render_assign(parent: Element, node: ast.Assign):
    assert node.type_comment is None
    print("assign")
    elt = add_node(parent, node, "row equal-sep gap")
    variables = add(elt, "row gap")
    for t in node.targets:
        expression.render(add(variables), t)
    if len(node.targets) > 1:
        variales.classes.append("parens comma-sep row gap")
    value = add(elt)
    expression.render(value, node.value)
    return
    #if len(targets) == 1:
    #    target = targets[0]
    #    return div(f"{target} = {value}")
    #else:
    #    return div(f"{tuple(targets)} = {value}")



def render_withitem(parent: Element, node: ast.withitem):
    elt = add_node(parent, node)
    if node.optional_vars:
        # add "<expr> as <name>"
        elt.classes.append("as-sep")
        elt.classes.append("row")
        expr = expression.render(elt, node.context_expr)
        name = expression.render(elt, node.optional_vars)
    else:
        # just add <expr>
        expr = expression.render(elt, node.context_expr)

def render_pass(parent: Element, node: ast.Pass):
    elt = add_node(parent, node, text="pass")

