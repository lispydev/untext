"""
statement rendering

from the official python AST documentation:
https://docs.python.org/3/library/ast.html
(at the time of writing, for python 3.14)


stmt = FunctionDef(identifier name, arguments args,
                   stmt* body, expr* decorator_list, expr? returns,
                   string? type_comment, type_param* type_params)
      | AsyncFunctionDef(identifier name, arguments args,
                         stmt* body, expr* decorator_list, expr? returns,
                         string? type_comment, type_param* type_params)

      | ClassDef(identifier name,
         expr* bases,
         keyword* keywords,
         stmt* body,
         expr* decorator_list,
         type_param* type_params)
      | Return(expr? value)

      | Delete(expr* targets)
      | Assign(expr* targets, expr value, string? type_comment)
      | TypeAlias(expr name, type_param* type_params, expr value)
      | AugAssign(expr target, operator op, expr value)
      -- 'simple' indicates that we annotate simple name without parens
      | AnnAssign(expr target, expr annotation, expr? value, int simple)

      -- use 'orelse' because else is a keyword in target languages
      | For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
      | AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
      | While(expr test, stmt* body, stmt* orelse)
      | If(expr test, stmt* body, stmt* orelse)
      | With(withitem* items, stmt* body, string? type_comment)
      | AsyncWith(withitem* items, stmt* body, string? type_comment)

      | Match(expr subject, match_case* cases)

      | Raise(expr? exc, expr? cause)
      | Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
      | TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
      | Assert(expr test, expr? msg)

      | Import(alias* names)
      | ImportFrom(identifier? module, alias* names, int? level)

      | Global(identifier* names)
      | Nonlocal(identifier* names)
      | Expr(expr value)
      | Pass | Break | Continue

      -- col_offset is the byte offset in the utf8 string the parser uses
      attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)
"""


# types
# HTML renderer -> no DOM needed
#from webview.dom.dom import DOM
#from webview.dom.element import Element
import ast

# html generation wrappers
from .html import node, text, element, debug, register_node
from . import html

# expressions can be found inside statements, but not the opposite
# (statement.py imports expression.py, but not the opposite)
from . import expression



"""
AST module rendering

(modules are not technically statements)
"""


def render_module(node: ast.Module):
    # unknown value
    assert len(node.type_ignores) == 0
    items = []
    for elt in node.body:
        # top-level strings are usually multiline
        # TODO: refactor to make the logic more explicit
        if isinstance(elt, ast.Expr) and isinstance(elt.value, ast.Constant) and isinstance(elt.value.value, str):
            lines = elt.value.value.split("\n")
            lines[0] = '"""' + lines[0]
            lines[-1] += '"""'
            lines = [line if line else "<br>" for line in lines]
            lines = [f"<div>{line}</div>" for line in lines]
            #items.append("".join(lines))
            items.append(html.text("".join(lines)))
            # failed implementation
            #rendered_text = elt.value.value.replace("\n", "</div><div>")
            #print(rendered_text)
            #print("\n" in rendered_text)
            #children.append(f'<div>"""</div><div>{elt.value.value}</div><div>"""</div>')
        else:
            items.append(render(elt))
    yield from element("module", *items)



"""
AST statement rendering

(the big switch)
"""


def render(node: ast.stmt):
    match type(node):
        case ast.FunctionDef:
            yield from render_funcdef(node)
        case ast.AsyncFunctionDef:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")

        case ast.ClassDef:
            yield from render_classdef(node)
        case ast.Return:
            yield from render_return(node)

        case ast.Delete:
            yield from render_delete(node)
        case ast.Assign:
            yield from render_assign(node)
        # 3.12+ feature
        # TODO: ignore it until pypy reaches 3.12 or stop supporting pypy
        #case ast.TypeAlias:
        #    raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.AugAssign:
            yield from render_augassign(node)
        case ast.AnnAssign:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")

        case ast.For:
            yield from render_for(node)
        case ast.AsyncFor:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.While:
            yield from render_while(node)
        case ast.If:
            yield from render_if(node)
        case ast.With:
            yield from render_with(node)
        case ast.AsyncWith:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")

        case ast.Match:
            yield from render_match(node)

        case ast.Raise:
            yield from render_raise(node)
        case ast.Try:
            # TODO: implement
            yield from render_try(node)
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.TryStar:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.Assert:
            yield from render_assert(node)

        case ast.Import:
            yield from render_import(node)
        case ast.ImportFrom:
            yield from render_importfrom(node)

        case ast.Global:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.Nonlocal:
            yield from render_nonlocal(node)
        case ast.Expr:
            # TODO: add a wrapper div, to type as a "expr in a statement"
            yield from expression.render(node.value)
        case ast.Pass:
            yield from render_pass(node)
        case ast.Break:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.Continue:
            yield from render_continue(node)

        # future python versions may add new things
        case default:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")



"""
AST statement rendering

(implementation for each type)
"""


@register_node
def render_funcdef(node: ast.FunctionDef):
    # supported features checks
    #assert len(node.decorator_list) == 0
    assert node.type_comment is None
    # 3.12+ feature
    # instead, see: type_comment
    # TODO: wait for pypy to reach 3.12 or explicitely stop supporting pypy
    #assert len(node.type_params) == 0

    # decorators
    decorators = [expression.render(d) for d in node.decorator_list]
    decorators = [element("at-prefix row", d) for d in decorators]
    # TODO: decide if subcomponents (decorator list, header, body)
    # should be annotated with classes or not
    decorators = element("decorators", *decorators)

    # header
    name = text(node.name)
    funcname = element("row def-prefix gap", name)
    params = render_parameters(node.args)
    funcparams = element("parens row", params)
    head = element("row", funcname, funcparams)
    if node.returns is not None:
        # "def f(...)" -> "def f(...) -> ..."
        funcreturn = expression.render(node.returns)
        head = html.items("row gap return-type-arrow-sep", "row gap",
                          [head, funcreturn])
    header = element("row colon-suffix", head)

    # body
    body = [render(stmt) for stmt in node.body]
    body_block = element("block", *body)

    yield from element("def", decorators, header, body_block)


# sub-part of render_funcdef
@register_node
def render_parameters(node: ast.arguments):
    # assertions and attribute parsing
    # TODO: support more cases
    assert len(node.posonlyargs) == 0
    # default values are for the last parameters
    # need to match argument names to default values with indices
    default_padding = len(node.args) - len(node.defaults)
    # flags (*args and **kwargs)
    assert node.kwarg is None

    params = []
    # normal args
    for i, param in enumerate(node.args):
        param = render_param(param)
        if i >= default_padding:
            # TODO: refactor the <param> = <value> rendering into render_param()
            default_value = node.defaults[i - default_padding]
            default_value = expression.render(default_value)
            param = html.items(
                "equal-sep row gap",
                "row gap",
                [param, default_value]
            )
        params.append(param)

    # vararg
    if node.vararg is not None:
        param = render_param(node.vararg)
        starred = element("star-prefix row", param)
        params.append(starred)

    # kwonly args (args that cannot be positional due to the vararg before them)

    # node.kwonlyargs are the parameters after the *vararg
    # the *vararg comes after normal (non-kwonly) parameters
    # their default values are in kw_defaults

    # node.kw_default contains default values for every kwonly arg,
    # with None when there is no default value
    for i, param in enumerate(node.kwonlyargs):
        param = render_param(param)
        if node.kw_defaults[i] is not None:
            default_value = node.kw_defaults[i]
            # items of a list with a separator need a wrapper to style the separator
            default_value = expression.render(default_value)
            param = html.items(
                "equal-sep row gap",
                "row gap",
                [param, default_value]
            )
        params.append(param)


    yield from html.items("parameters comma-sep row", "row gap", params)


# sub-part of render_parameters
@register_node
def render_param(node: ast.arg):
    assert node.type_comment is None

    param_name = text(node.arg)
    # used to indicate the structure of the html:
    param_name = element("parameter-name", param_name)
    if node.annotation is None:
        #param_name = element("bg-red", param_name)
        yield from param_name
        return

    annotation = expression.render(node.annotation)
    name = element("row colon-suffix", param_name)
    param = element("parameter row gap", name, annotation)
    yield from param


def render_classdef(node: ast.ClassDef):
    # TODO: support decorators
    # TODO: support type_params
    assert not node.decorator_list

    # decorators
    # TODO:
    decorators = element("")

    # header
    name = text(node.name)
    kwargs = [expression.render(kwarg) for kwarg in node.keywords]
    args = [expression.render(arg) for arg in node.bases]
    if kwargs or args:
        arguments = html.items("comma-sep row", "row gap", [*kwargs, *args])
        arguments = element("parens row", arguments)
    else:
        arguments = element("")
    header = element("row", name, arguments)
    header = element("class-prefix row gap", header)
    header = element("row colon-suffix", header)

    # body
    body = [render(stmt) for stmt in node.body]
    body = element("block", *body)

    yield from element("class", decorators, header, body)


@register_node
def render_return(node: ast.Return):
    if node.value is not None:
        value = expression.render(node.value)
    else:
        value = text("")
    yield from element("return return-prefix row gap", value)


@register_node
def render_delete(node: ast.Delete):
    # example: del a, b, c
    items = [expression.render(target) for target in node.targets]
    items = html.items("comma-sep row", "row gap bg-red", items)
    yield from element("delete del-prefix row gap bg-red", items)


@register_node
def render_assign(node: ast.Assign):
    assert node.type_comment is None

    value = expression.render(node.value)
    targets = [expression.render(t) for t in node.targets]
    # display the value as the last (equal-separated) target
    targets.append(value)
    formatted = html.items("assign equal-sep row gap", "row gap", targets)
    yield from formatted



# augassign:
#targ = render_expr(node.target)
#op = render_binaryop(node.op)
#val = render_expr(node.value)
#return f"{targ} {op}= {val}"

# TODO: fix: the operator must be displayed
# format: <node> <op>= <node>
# <node><gap><op>=<gap><node>
# (<node> (<op>=) <node>)
def render_augassign(node: ast.AugAssign):
    target = expression.render(node.target)
    operator = text(expression.read_binaryop(node.op))
    # hack: add an empty div to force the = separator to render
    # TODO?: add a .equal-suffix css class
    empty = element("")
    operator = html.items("equal-sep row", "row", [operator, empty])
    val = expression.render(node.value)
    yield from element("row gap", target, operator, val)


@register_node
def render_for(node: ast.For):
    assert node.type_comment is None

    # header
    # example: "for x in lst:"
    variable = expression.render(node.target)  # "x"
    iterator = expression.render(node.iter)  # "lst"
    # "x in lst"
    # TODO: could fit .for-prefix here
    header = html.items("in-sep row gap", "row gap",
                                [variable, iterator])
    # "for x in lst"
    header = element("for-prefix row gap", header)
    # "for x in lst:"
    header = element("colon-suffix row", header)

    body = [render(stmt) for stmt in node.body]
    body = element("block", *body)


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

    yield from element("for", header, body)



@register_node
def render_while(node: ast.While):
    test = expression.render(node.test)
    header = element("while-prefix row gap", test)
    header = element("colon-suffix row", header)

    body = [render(stmt) for stmt in node.body]
    body = element("block", *body)

    assert not node.orelse
    # if node.orelse:
    #else_body = [render(stmt) for stmt in node.orelse]
    yield from element("while", header, body)


@register_node
def render_if(node: ast.If):
    if is_elif(node):
        yield from render_elifs(node)
        return

    test = expression.render(node.test)
    header = element("row gap if-prefix", test)
    header = element("row colon-suffix", header)

    if_body = [render(stmt) for stmt in node.body]
    if_block = element("block", *if_body)

    parts = [header, if_block]

    if node.orelse:
        else_header = element("row colon-suffix else-prefix")
        else_body = [render(stmt) for stmt in node.orelse]
        else_block = element("block", *else_body)
        parts.append(else_header)
        parts.append(else_block)
    yield from element("if", *parts)


# helpers for elifs
# internally, Python represents elifs as nested else: if:
def is_elif(if_node: ast.If):
    "return True if the if has an elif branch"
    # if/elif gets compiled to if/else{if}
    # if/elif/else gets compiled to if/else{if/else}
    if len(if_node.orelse) != 1:
        return False
    return isinstance(if_node.orelse[0], ast.If)

def elif_depth(if_node: ast.If):
    "return the number of elif branches in an if"
    n = 0
    while is_elif(if_node):
        n += 1
        if_node = if_node.orelse[0]
    return n

def collect_branches(if_node: ast.If):
    n = elif_depth(if_node)
    branches = []
    for i in range(n):
        condition = if_node.test
        body = if_node.body
        branches.append((condition, body))
        if_node = if_node.orelse[0]
    # final else (not if) branch
    if if_node.orelse:
        assert not isinstance(if_node.orelse[0], ast.If)
    # the last element is not a (cond, body) tuple
    branches.append(if_node.orelse)
    return branches


# the node registering is already done by render_if()
def render_elifs(if_node: ast.If):
    branches = collect_branches(if_node)
    if_branch, *elif_branches, else_body = branches


    blocks = []

    # if
    test, body = if_branch
    test = expression.render(test)
    header = element("row gap if-prefix", test)
    header = element("row colon-suffix", header)

    body = [render(stmt) for stmt in body]
    body = element("block", *body)

    if_block = element("if-block", header, body)
    blocks.append(if_block)

    # elifs
    for (test, body) in elif_branches:
        test = expression.render(test)
        header = element("row gap elif-prefix", test)
        header = element("row colon-suffix", header)

        body = [render(stmt) for stmt in body]
        body = element("block", *body)

        elif_block = element("elif-block", header, body)
        blocks.append(elif_block)

    # else
    if else_body:
        header = element("row else-prefix colon-suffix")
        body = [render(stmt) for stmt in else_body]
        body = element("block", *body)
        else_block = element("else-block", header, body)
        blocks.append(else_block)
        #header = add(else_elt, "row colon-suffix")
        #header_content = add(header, "row gap else-prefix")

    # TODO: see if render_if() and render_elif() can return the same html layou
    # if possible, use the same .if class for both
    yield from element("elif", *blocks)


@register_node
def render_with(node: ast.With):
    assert node.type_comment is None
    assert len(node.items) == 1  # TODO: test with more cases
    items = [render_withitem(item) for item in node.items]
    body = [render(stmt) for stmt in node.body]
    block = element("block", *body)
    header = element("with-prefix row gap", *items)
    header = element("row colon-suffix", header)
    yield from element("with", header, block)


@register_node
def render_withitem(node: ast.withitem):
    if node.optional_vars:
        # "<expr> as <name>"
        expr = expression.render(node.context_expr)
        name = expression.render(node.optional_vars)
        item = html.items("as-sep row gap", "row gap", [expr, name])
    else:
        # just "<expr>"
        item = expression.render(node.context_expr)
    yield from element("with-item", item)


def render_match(node: ast.Match):
    yield from element("bg-red", text("match"))
    return
    elt = add_node(parent, node)
    header = add(elt)
    colon_suffix = add(header, "colon-suffix row")
    match_prefix = add(colon_suffix, "match-prefix row gap")
    matched_value = expression.render(match_prefix, node.subject)

    cases = add(elt, "block")
    for case in node.cases:
        render_case(cases, case)

    return elt

# part of render_match
def render_case(node: ast.match_case):
    yield from element("bg-red", text("case"))
    return
    # TODO: support more cases
    assert node.guard is None
    elt = add_node(parent, node)
    header = add(elt, "row colon-suffix")
    content = add(header, "row gap case-prefix")
    # turns out match patterns are not actually expressions,
    # despite having the same syntax
    render_pattern(content, node.pattern)

    body = add(elt, "block")
    for stmt in node.body:
        render(body, stmt)

# TODO: implement missing cases
def render_pattern(node: ast.pattern):
    yield from element("bg-red", text("pattern"))
    return
    match type(node):
        case ast.MatchValue:
            return render_match_value(parent, node)
        case ast.MatchSingleton:
            return render_match_singleton(parent, node)
        case ast.MatchSequence:
            return render_match_sequence(parent, node)
        case ast.MatchMapping:
            return render_match_mapping(parent, node)
        case ast.MatchClass:
            return render_match_class(parent, node)

        case ast.MatchStar:
            return render_match_star(parent, node)

        case ast.MatchAs:
            return render_match_as(parent, node)
        case ast.MatchOr:
            return render_match_or(parent, node)

        case default:
            raise ValueError(f"Unexpected match pattern type: {type(node)}")


def render_match_value(node: ast.MatchValue):
    yield from element("bg-red", text("match_value"))
    return
    elt = add_node(parent, node)
    expression.render(elt, node.value)

def render_match_as(node: ast.MatchAs):
    yield from element("bg-red", text("match_as"))
    return
    # TODO: support other cases
    # case [x] as y:
    # case default:     <--- the only kind used

    # specific to case default:
    assert node.pattern is None
    assert node.name == "default"
    elt = add_node(parent, node)
    add_text(elt, node.name)
    return elt



def render_raise(node: ast.Raise):
    # TODO: check if support for this attribute is needed
    assert node.cause is None
    raised = expression.render(node.exc)
    yield from element("raise raise-prefix row gap", raised)


def render_assert(node: ast.Assert):
    # TODO: support assertion messages
    assert node.msg is None
    asserted = expression.render(node.test)
    yield from element("assert assert-prefix row gap", asserted)


# TODO: rewrite
def render_import(node: ast.Import):
    aliases = []
    for name in node.names:
        continue
        aliases.append(
            element(
                "row gap",
                render_alias(name)
            )
        )
    yield from html.node(
        node,
        element(
            "import import-prefix row",
            element(
                "aliases row comma-sep",
                #*aliases,
                *[element("row gap", render_alias(name))
                    for name in node.names]
            )
        )
    )

# sub-part of import and importfrom nodes
def render_alias(node: ast.alias):
    if node.asname is not None:
        alias = html.element(
            "named-alias import-alias as-sep row gap",
            html.element("row gap", html.text(node.name)),
            html.element("row gap", html.text(node.asname))
        )
    else:
        alias = html.element(
            "unnamed-alias",
            html.text(node.name)
        )
    yield from html.node(
        node,
        html.element(
            "alias row",
            alias
        )
    )


def render_importfrom(node: ast.ImportFrom):
    # build the html bottom-up
    # example: from ..a import b, c as d

    # ".."
    import_level = html.text("." * node.level)
    # "a"
    from_module = html.text(node.module or "")
    # ["b", "c as d"]
    imported = [render_alias(name) for name in node.names]
    # (comma separated) list items must be wrapped for styling separators
    imported = [html.element("row gap", x) for x in imported]

    # "b, c as d"
    imported_field = html.element("aliases row comma-sep", *imported)
    # "..a"
    from_field = html.element("row", import_level, from_module)

    # "import b, c as d"
    import_part = html.element("import-prefix row gap", imported_field)
    # "from ..a"
    from_part = html.element("from-prefix row gap", from_field)

    import_statement = html.element("importfrom row gap", from_part, import_part)
    yield from html.node(node, import_statement)




def render_nonlocal(node: ast.Nonlocal):
    yield from element("bg-red", text("nonlocal"))
    return
    elt = add_node(parent, node, "row gap nonlocal-prefix")
    names = add(elt, "row comma-sep")
    for name in node.names:
        add(names, "row gap", name)


def render_pass(node: ast.Pass):
    yield from html.node(node, text("pass"))


def render_continue(node: ast.Continue):
    yield from html.node(node, text("continue"))

