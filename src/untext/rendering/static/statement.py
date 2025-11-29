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
from .html import node, text, element
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
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.Expr:
            # TODO: wrapper div ? to type as a "expr in a statement"
            #yield from expression.render(node)
            yield ""
            return
        case ast.Pass:
            yield from render_pass(node)
        case ast.Break:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")
        case ast.Continue:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")

        # future python versions may add new things
        case default:
            raise ValueError(f"Unexpected ast statement type: {type(node)}")



"""
AST statement rendering

(implementation for each type)
"""


def render_funcdef(node: ast.FunctionDef):
    yield ""
    return
    # 3.12+ feature
    # instead, see: type_comment
    # TODO: wait for pypy to reach 3.12 or explicitely stop supporting pypy
    #assert len(node.type_params) == 0
    assert len(node.decorator_list) == 0
    assert node.type_comment is None
    elt = add_node(parent, node, "funcdef")

    header = add(elt, "row colon-suffix")
    spaced_signature = add(header, "row gap return-type-arrow-sep")
    left = add(spaced_signature, "row")
    funcname = add(left, "row gap def-prefix", node.name)
    params = add(left, "parens row")
    if node.returns is not None:
        right = add(spaced_signature, "row gap")
        expression.render(right, node.returns)
    #params_content = add(params, "comma-sep row gap")
    render_parameters(params, node.args)
    body = add(elt, "block")

    for stmt in node.body:
        render(body, stmt)
    return elt


# sub-part of render_funcdef
def render_parameters(node: ast.arguments):
    yield ""
    return
    # TODO: support more cases
    assert len(node.posonlyargs) == 0
    assert len(node.kwonlyargs) == 0
    assert len(node.kw_defaults) == 0
    # default values are for the last parameters
    # need to match argument names to default values with indices
    default_padding = len(node.args) - len(node.defaults)
    # flags (*args and **kwargs)
    assert node.vararg is None
    assert node.kwarg is None
    elt = add(parent, "comma-sep row")
    for i, param in enumerate(node.args):
        comma_separated_item = add(elt, "row gap")
        if i >= default_padding:
            param_elt = add(comma_separated_item, "equal-sep row gap")
            render_param(param_elt, param)
            expression.render(add(param_elt, "row gap"), node.defaults[i - default_padding])
        else:
            render_param(comma_separated_item, param)
    #result = ", ".join([render_arg(arg) for arg in node.args])
    #return result
    return elt

# sub-part of render_parameters
def render_param(node: ast.arg):
    yield ""
    return
    assert node.type_comment is None
    # text metadata (not needed in a no-text IDE)
    #print(arg.lineno)
    #print(arg.col_offset)
    #print(arg.end_lineno)
    #print(arg.end_col_offset)

    # comma-separated items must be inlined,
    # so that the comma is on the same line
    elt = add_node(parent, node, "row")
    if node.annotation is None:
        add(elt, text=node.arg)
    else:
        typed_group = add(elt, "row gap")
        name = add(typed_group, "row colon-suffix", text=node.arg)
        expression.render(typed_group, node.annotation)
    return elt

def render_classdef(node: ast.ClassDef):
    yield ""
    return
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
        arguments = add(paren_wrapped, "comma-sep row")
        for kwarg in node.keywords:
            expression.render_keyword_arg(add(arguments, "row gap"), kwarg)
        for base in node.bases:
            expression.render(add(arguments, "row gap"), base)

    body = add(elt, "block")
    for stmt in node.body:
        render(body, stmt)
    return elt

def render_return(node: ast.Return):
    yield ""
    return
    elt = add_node(parent, node, "return-prefix row gap")
    if node.value is not None:
        expression.render(elt, node.value)
    return elt


def render_delete(node: ast.Delete):
    yield ""
    return
    elt = add_node(parent, node)
    del_prefixed = add(elt, "del-prefix row gap")
    elts = add(del_prefixed, "comma-sep row")
    for target in node.targets:
        item = add(elts, "row gap")
        expression.render(item, target)


def render_assign(node: ast.Assign):
    yield ""
    return
    assert node.type_comment is None
    # TODO: support multiple targets
    # example:
    # a = b = 1
    assert len(node.targets) == 1
    elt = add_node(parent, node, "row equal-sep gap")
    variables = add(elt, "row gap")
    #for t in node.targets:
    expression.render(variables, node.targets[0])
    value = add(elt, "row gap")
    expression.render(value, node.value)
    return
    #if len(targets) == 1:
    #    target = targets[0]
    #    return div(f"{target} = {value}")
    #else:
    #    return div(f"{tuple(targets)} = {value}")
    return elt



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
    yield ""
    return
    elt = add_node(parent, node, "row gap")
    target = expression.render(add(elt), node.target)
    # hack: add an empty div to force the = separator to render
    # TODO?: add a .equal-suffix css class
    assign_operator = add(elt, "equal-sep row")
    add(assign_operator, text=expression.read_binaryop(node.op))
    add(assign_operator, "row")
    #op = expression.read_binaryop(node.op)
    #elt.classes.append(f"{op}-sep")
    val = expression.render(add(elt), node.value)
    return elt



def render_for(node: ast.For):
    yield ""
    return
    assert node.type_comment is None
    elt = add_node(parent, node)
    header = add(elt, "row colon-suffix")
    prefixed = add(header, "for-prefix in-sep row gap")
    # separators like in-sep need an additional div (add(elt)) to add the separator as a suffix of this wrapper div
    target = expression.render(prefixed, node.target)
    iterator = expression.render(add(prefixed, "row gap"), node.iter)

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



def render_while(node: ast.While):
    yield ""
    return
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

def render_if(node: ast.If):
    yield ""
    return
    elt = add_node(parent, node)
    if is_elif(node):
        return render_elifs(elt, node)
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

def render_elifs(elt, if_node: ast.If):
    branches = collect_branches(if_node)
    if_branch, *elif_branches, else_body = branches


    # if
    if_test, if_body = if_branch
    if_elt = add(elt)
    header = add(if_elt, "row colon-suffix")
    header_content = add(header, "row gap if-prefix")
    _if_test = expression.render(header_content, if_test)

    body = add(if_elt, "block")
    for stmt in if_body:
        render(body, stmt)

    # elifs
    for (test, ast_body) in elif_branches:
        elif_elt = add(elt)
        header = add(elif_elt, "row colon-suffix")
        header_content = add(header, "row gap elif-prefix")
        _test = expression.render(header_content, test)
        body = add(elif_elt, "block")
        for stmt in ast_body:
            render(body, stmt)

    # else
    if else_body:
        else_elt = add(elt)
        header = add(else_elt, "row colon-suffix")
        header_content = add(header, "row gap else-prefix")
        body = add(else_elt, "block")
        for stmt in else_body:
            render(body, stmt)

    return elt


def render_with(node: ast.With):
    yield ""
    return
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

def render_withitem(node: ast.withitem):
    yield ""
    return
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



def render_match(node: ast.Match):
    yield ""
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
    yield ""
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
    yield ""
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
    yield ""
    return
    elt = add_node(parent, node)
    expression.render(elt, node.value)

def render_match_as(node: ast.MatchAs):
    yield ""
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
    yield ""
    return
    # TODO: check if support for this attribute is needed
    assert node.cause is None
    elt = add_node(parent, node, "raise-prefix row gap")
    expression.render(elt, node.exc)
    return elt


def render_assert(node: ast.Assert):
    yield ""
    return
    # TODO: support assertion messages
    assert node.msg is None
    elt = add_node(parent, node, "assert-prefix gap row")
    expression.render(elt, node.test)
    return elt

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
    yield ""
    return
    elt = add_node(parent, node, "importfrom row gap")

    # prefixed items need .row and .gap to space their prefix and content
    from_prefixed = add(elt, "from-prefix row gap")
    from_content = add(from_prefixed, "row")
    relative_level = add_text(from_content, "." * node.level)
    if node.module is not None:
        from_field = add_text(from_content, node.module)

    import_prefixed = add(elt, "import-prefix row gap")
    aliases = add(import_prefixed, "aliases row comma-sep")
    for name in node.names:
        render_alias(add(aliases, "row gap"), name)
    return elt




def render_nonlocal(node: ast.Nonlocal):
    yield ""
    return
    elt = add_node(parent, node, "row gap nonlocal-prefix")
    names = add(elt, "row comma-sep")
    for name in node.names:
        add(names, "row gap", name)


def render_pass(node: ast.Pass):
    yield ""
    return
    elt = add_node(parent, node, text="pass")
    return elt


