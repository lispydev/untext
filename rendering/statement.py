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
            return render_funcdef(parent, node)
        case ast.AsyncFunctionDef:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncFunctionDef")
        case ast.ClassDef:
            return render_classdef(parent, node)
        case ast.Return:
            return render_return(parent, node)

        case ast.Delete:
            raise NotImplementedError("statement.render() not implemented for ast.Delete")
        case ast.Assign:
            return render_assign(parent, node)
        # 3.12+ feature
        # TODO: ignore it until pypy reaches 3.12 or stop supporting pypy
        # case ast.TypeAlias:
        #     raise NotImplementedError("statement.render() not implemented for ast.TypeAlias")
        case ast.AugAssign:
            return render_augassign(parent, node)
        case ast.AnnAssign:
            raise NotImplementedError("statement.render() not implemented for ast.AnnAssign")

        case ast.For:
            return render_for(parent, node)
        case ast.AsyncFor:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncFor")
        case ast.While:
            return render_while(parent, node)
        case ast.If:
            return render_if(parent, node)
        case ast.With:
            return render_with(parent, node)
        case ast.AsyncWith:
            raise NotImplementedError("statement.render() not implemented for ast.AsyncWith")

        case ast.Match:
            raise NotImplementedError("statement.render() not implemented for ast.Match")

        case ast.Raise:
            return render_raise(parent, node)
        case ast.Try:
            raise NotImplementedError("statement.render() not implemented for ast.Try")
        case ast.TryStar:
            raise NotImplementedError("statement.render() not implemented for ast.TryStar")
        case ast.Assert:
            return render_assert(parent, node)

        case ast.Import:
            return render_import(parent, node)
        case ast.ImportFrom:
            return render_importfrom(parent, node)

        case ast.Global:
            raise NotImplementedError("statement.render() not implemented for ast.Global")
        case ast.Nonlocal:
            raise NotImplementedError("statement.render() not implemented for ast.Nonlocal")
        case ast.Expr:
            return expression.render(parent, node.value)
            #raise NotImplementedError("statement.render() not implemented for ast.Expr")
        case ast.Pass:
            return render_pass(parent, node)
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
def render_module(parent: Element, node: ast.Module) -> Element:
    elt = add_node(parent, node)
    for stmt in node.body:
        render(elt, stmt)
    return elt


"""
AST statement node rendering
"""

def render_raise(parent: Element, node: ast.Raise) -> Element:
    # TODO: check if support for this attribute is needed
    assert node.cause is None
    elt = add_node(parent, node, "raise-prefix row gap")
    expression.render(elt, node.exc)
    return elt


def render_assert(parent: Element, node: ast.Assert) -> Element:
    # TODO: support assertion messages
    assert node.msg is None
    elt = add_node(parent, node, "assert-prefix gap row")
    expression.render(elt, node.test)
    return elt

def render_import(parent: Element, node: ast.Import) -> Element:
    elt = add_node(parent, node, "import import-prefix row")
    aliases = add(elt, "aliases row comma-sep gap")
    for name in node.names:
        #comma_separated_item = add(aliases, "row")
        render_alias(aliases, name)
    return elt

# sub-part of import and importfrom nodes
def render_alias(parent: Element, node: ast.alias) -> Element:
    elt = add_node(parent, node, "alias row")
    if node.asname is not None:
        # create an alias (div (div name) "as" (div asname))
        alias = add(elt, "import-alias as-sep row gap")
        name = add_text(add(alias, "row gap"), node.name)
        asname = add_text(add(alias, "row gap"), node.asname)
    else:
        # TODO: find a class name for "unaliased import"
        alias = add(elt)
        name = add_text(alias, node.name)
    return elt


def render_importfrom(parent: Element, node: ast.ImportFrom) -> Element:
    assert node.level == 0
    elt = add_node(parent, node, "importfrom row gap")

    # prefixed items need .row and .gap to space their prefix and content
    from_prefixed = add(elt, "from-prefix row gap")
    from_field = add_text(from_prefixed, node.module)

    import_prefixed = add(elt, "import-prefix row gap")
    aliases = add(import_prefixed, "aliases row comma-sep gap")
    for name in node.names:
        render_alias(aliases, name)
    return elt


def render_funcdef(parent: Element, node: ast.FunctionDef) -> Element:
    # 3.12+ feature
    # instead, see: type_comment
    # TODO: wait for pypy to reach 3.12 or explicitely stop supporting pypy
    #assert len(node.type_params) == 0
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
    return elt


# sub-part of render_funcdef
def render_parameters(parent: Element, node: ast.arguments) -> Element:
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
    return elt

# sub-part of render_parameters
def render_param(parent: Element, node: ast.arg) -> Element:
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
    return elt

def render_classdef(parent: Element, node: ast.ClassDef) -> Element:
    # TODO: support decorators
    # TODO: support type_params
    assert not node.decorator_list
    elt = add_node(parent, node)
    # header
    colon_suffixed = add(elt, "row colon-suffix")
    class_prefixed = add(colon_suffixed, "class-prefix row gap")
    header_content = add(class_prefixed, "row")
    name = add(header_content, text=node.name)
    if node.keywords or node.bases:
        paren_wrapped = add(header_content, "parens row")
        arguments = add(paren_wrapped, "comma-sep row gap")
        for kwarg in node.keywords:
            expression.render_keyword_arg(add(arguments, "row"), kwarg)
        for base in node.bases:
            expression.render(add(arguments, "row"), base)

    body = add(elt, "block")
    for stmt in node.body:
        render(body, stmt)
    return elt

def render_return(parent: Element, node: ast.Return) -> Element:
    elt = add_node(parent, node, "return-prefix row gap")
    if node.value is not None:
        expression.render(elt, node.value)
    return elt

def render_assign(parent: Element, node: ast.Assign) -> Element:
    assert node.type_comment is None
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
    return elt


# TODO: fix: the operator must be displayed
# format: <node> <op>= <node>
# <node><gap><op>=<gap><node>
# (<node> (<op>=) <node>)
def render_augassign(parent: Element, node: ast.AugAssign) -> Element:
    elt = add_node(parent, node, "row gap")
    target = expression.render(add(elt), node.target)
    assign_operator = add(elt, "equal-sep")
    add(assign_operator, "row", expression.read_binaryop(node.op))
    add(assign_operator)
    #op = expression.read_binaryop(node.op)
    #elt.classes.append(f"{op}-sep")
    val = expression.render(add(elt), node.value)
    return elt



def render_for(parent: Element, node: ast.For) -> Element:
    assert node.type_comment is None
    elt = add_node(parent, node)
    header = add(elt, "row colon-suffix")
    prefixed = add(header, "for-prefix in-sep row gap")
    # separators like in-sep need an additional div (add(elt)) to add the separator as a suffix of this wrapper div
    target = expression.render(add(prefixed, "row gap"), node.target)
    iterator = expression.render(add(prefixed, "row"), node.iter)

    # TODO: WIP, debug later
    body = add(elt, "block")
    for stmt in node.body:
        render(body, stmt)

    # TODO: process for: else: blocks
    # (add more headers after the main body)
    assert not node.orelse
    #parts = [block]
    #if node.orelse:
    #    else_header = div("else:")
    #    else_body = [render_statement(statement) for statement in node.orelse]
    #    else_body = block("".join(else_body))
    #    else_block = div(else_header + else_body)
    #    parts.append(else_block)

    #result = "".join(parts)
    #return div(result)


    return elt



def render_while(parent: Element, node: ast.While) -> Element:
    elt = add_node(parent, node)
    header = add(elt, "colon-suffix row")
    header_content = add(header, "while-prefix row gap")
    test = expression.render(header_content, node.test)
    body = add(elt, "block")
    for stmt in node.body:
        render(body, stmt)
    assert not node.orelse
    # if node.orelse:
    #else_body = [render_statement(statement) for statement in node.orelse]
    return elt

def render_if(parent: Element, node: ast.If) -> Element:
    elt = add_node(parent, node)
    header = add(elt, "row colon-suffix")
    header_content = add(header, "row gap if-prefix")
    expression.render(header_content, node.test)
    block = add(elt, "block")
    for stmt in node.body:
        render(block, stmt)
    if node.orelse:
        else_header = add(elt, "row colon-suffix else-prefix")
        else_block = add(elt, "block")
        for stmt in node.orelse:
            render(else_block, stmt)

    return elt

    # TODO: process elifs

    ## manual processing
    ## the Python AST represent elif branches as nested else: if
    #if is_elif(node):
    #    #print("found elif")
    #    return render_elifs(node)
    #test = render_expr(node.test)
    #body = [render_statement(s) for s in node.body]

    #if_header = div(f"if {test}:")
    #body = block("".join(body))

    #ifpart = div(if_header + body)

    #parts = [ifpart]

    #if node.orelse:
    #    else_header = f"<div>else:</div>"
    #    else_body = [render_statement(s) for s in node.orelse]
    #    else_body = "".join(else_body)
    #    else_body = f"<div style='margin-left: 30px'>{else_body}</div>"

    #    elsepart = f"<div>{else_header}{else_body}</div>"
    #    parts.append(elsepart)
    #return "".join(parts)

def render_with(parent: Element, node: ast.With) -> Element:
    assert node.type_comment is None
    elt = add_node(parent, node)
    # this breaks if newlines are added for clarity:
    #header = elt.append("""<div class="with-prefix colon-suffix row gap"></div>""")
    header = add(elt)
    colon_suffixed = add(header, "row colon-suffix")
    header_content = add(colon_suffixed, "with-prefix row gap")
    #print(header)
    body = add(elt, "block")
    for item in node.items:
        render_withitem(header_content, item)
    for stmt in node.body:
        render(body, stmt)
    return elt

def render_withitem(parent: Element, node: ast.withitem) -> Element:
    elt = add_node(parent, node)
    if node.optional_vars:
        # add "<expr> as <name>"
        named = add(elt, "as-sep row gap")
        expr = expression.render(add(named, "row gap"), node.context_expr)
        name = expression.render(add(named, "row gap"), node.optional_vars)
    else:
        # just add <expr>
        unnamed = add(elt)
        expr = expression.render(unnamed, node.context_expr)
    return elt

def render_pass(parent: Element, node: ast.Pass) -> Element:
    elt = add_node(parent, node, text="pass")
    return elt

