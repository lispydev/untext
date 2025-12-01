"""
expression rendering

from the official python documentation:
https://docs.python.org/3/library/ast.html
(at the time of writing, for python 3.14)


expr = BoolOp(boolop op, expr* values)
    | NamedExpr(expr target, expr value)
    | BinOp(expr left, operator op, expr right)
    | UnaryOp(unaryop op, expr operand)
    | Lambda(arguments args, expr body)
    | IfExp(expr test, expr body, expr orelse)
    | Dict(expr?* keys, expr* values)
    | Set(expr* elts)
    | ListComp(expr elt, comprehension* generators)
    | SetComp(expr elt, comprehension* generators)
    | DictComp(expr key, expr value, comprehension* generators)
    | GeneratorExp(expr elt, comprehension* generators)
    -- the grammar constrains where yield expressions can occur
    | Await(expr value)
    | Yield(expr? value)
    | YieldFrom(expr value)
    -- need sequences for compare to distinguish between
    -- x < 4 < 3 and (x < 4) < 3
    | Compare(expr left, cmpop* ops, expr* comparators)
    | Call(expr func, expr* args, keyword* keywords)
    | FormattedValue(expr value, int conversion, expr? format_spec)
    | Interpolation(expr value, constant str, int conversion, expr? format_spec)
    | JoinedStr(expr* values)
    | TemplateStr(expr* values)
    | Constant(constant value, string? kind)

    -- the following expression can appear in assignment context
    | Attribute(expr value, identifier attr, expr_context ctx)
    | Subscript(expr value, expr slice, expr_context ctx)
    | Starred(expr value, expr_context ctx)
    | Name(identifier id, expr_context ctx)
    | List(expr* elts, expr_context ctx)
    | Tuple(expr* elts, expr_context ctx)

    -- can appear only in Subscript
    | Slice(expr? lower, expr? upper, expr? step)

    -- col_offset is the byte offset in the utf8 string the parser uses
    attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)
"""


from webview.dom.element import Element
import ast

import html
import json

#from untext.rendering.html import register, div, add_node, add, add_text, add_pre
from .html import node, text, element, debug, register_node
from . import html


def render(node: ast.expr):
    match type(node):
        case ast.BoolOp:
            yield from render_boolop(node)
        case ast.NamedExpr:
            raise NotImplementedError('expression.render() not implemented for ast.NamedExpr')
        case ast.BinOp:
            yield from render_binop(node)
        case ast.UnaryOp:
            yield from render_unaryop(node)
        case ast.Lambda:
            raise NotImplementedError('expression.render() not implemented for ast.Lambda')
        case ast.IfExp:
            yield from render_ifexp(node)
        case ast.Dict:
            yield from render_dict(node)
        case ast.Set:
            raise NotImplementedError('expression.render() not implemented for ast.Set')
        case ast.ListComp:
            yield from render_list_comprehension(node)
        case ast.SetComp:
            raise NotImplementedError('expression.render() not implemented for ast.SetComp')
        case ast.DictComp:
            raise NotImplementedError('expression.render() not implemented for ast.DictComp')
        case ast.GeneratorExp:
            raise NotImplementedError('expression.render() not implemented for ast.GeneratorExp')
        case ast.Await:
            raise NotImplementedError('expression.render() not implemented for ast.Await')
        case ast.Yield:
            yield from render_yield(node)
        case ast.YieldFrom:
            yield from render_yieldfrom(node)
        case ast.Compare:
            yield from render_compare(node)
        case ast.Call:
            yield from render_call(node)
        case ast.FormattedValue:
            yield from render_formatted_value(node)
        # case ast.Interpolation:
        #     raise NotImplementedError('expression.render() not implemented for ast.Interpolation')
        case ast.JoinedStr:
            yield from render_joinedstr(node)
        # case ast.TemplateStr:
        #     raise NotImplementedError('expression.render() not implemented for ast.TemplateStr')
        case ast.Constant:
            yield from render_constant(node)
        case ast.Attribute:
            yield from render_attribute(node)
        case ast.Subscript:
            yield from render_subscript(node)
        case ast.Starred:
            yield from render_starred(node)
        case ast.Name:
            yield from render_name(node)
        case ast.List:
            yield from render_list(node)
        case ast.Tuple:
            yield from render_tuple(node)
        case ast.Slice:
            yield from render_slice(node)
        case default:
            raise ValueError(f"Unexpected ast expression type: {type(node)}")


"""
AST expression rendering

(implementation for each type)
"""


@register_node
def render_boolop(node: ast.BoolOp):
    values = [render(v) for v in node.values]
    result = html.items(f"row gap {read_boolop(node.op)}-sep", "row gap", values)
    yield from result


"""
this code uses html data-attributes to encode the operator, and css to render it dynamically

the html output in theory:
<div class="operation" data-operator="+">
  <div class="operand">a</div>
  <div class="operand">b</div>
</div>

in practice, css support is lacking, so we need this:
<div class="operation" data-operator="+">
  <div class="operand" data-operator="+">a<div>
  <div class="operand">b</div>
</div>
"""
def render_binop(node: ast.BinOp):
    yield from element("bg-red", text("binop"))
    return
    elt = add_node(parent, node, "operation row gap")
    elt.attributes["data-operator"] = read_binaryop(node.op)
    operator_suffixed = add(elt, "row gap op-suffixed")
    # note: setting css variables from the DOM API is a pain
    # recent versions of pywebview do not have the same syntax for setting css properties

    # this code works in every version, but very ugly
    #webview.windows[1].evaluate_js(f"""
    #document.getElementById('{node.node_id}').style.setProperty('--operator', '"+"')
    #""")

    # this does NOT work in cpython with apt-packaged pywebview, but almost
    #operator_suffixed.style["--operator"] = f'\\"{read_binaryop(node.op)}\\"'

    # this works in pypy with pip-packaged pywebview, but pywebview is complicated to install without distro packaging
    #operator_suffixed.style["--operator"] = json.dumps(f'"{read_binaryop(node.op)}"')

    # the easy solution is to never set css variables from python:
    left = render(elt, node.left)
    operator_prefixed = add(elt, "row gap")
    operator_prefixed.attributes["data-operator"] = read_binaryop(node.op)
    right = render(operator_prefixed, node.right)
    #operator_suffixed.attributes["data-operator"] = read_binaryop(node.op)
    #left = render(operator_suffixed, node.left)
    #right = render(add(elt, "row gap"), node.right)
    return elt

def read_binaryop(op: ast.operator):
    # css classes cannot have special characters like +
    if isinstance(op, ast.Add):
        return "+"
    elif isinstance(op, ast.Sub):
        return "-"
    elif isinstance(op, ast.Mult):
        return "*"
    elif isinstance(op, ast.Div):
        pass
    elif isinstance(op, ast.FloorDiv):
        pass
    elif isinstance(op, ast.Mod):
        pass
    elif isinstance(op, ast.Pow):
        pass
    elif isinstance(op, ast.LShift):
        pass
    elif isinstance(op, ast.RShift):
        pass
    elif isinstance(op, ast.BitOr):
        return "|"
    elif isinstance(op, ast.BitXor):
        pass
    elif isinstance(op, ast.BitAnd):
        pass
    elif isinstance(op, ast.MatMult):
        pass
    raise NotImplementedError(f"unknown binary operator: {op}")


# TODO: go back to previous "operator separators" and replace them by DOM nodes
# (operators have semantic meaning, they are not just syntax)
# (keep the css for infix inlining if needed)
def render_unaryop(node: ast.UnaryOp):
    yield from element("bg-red", text("unaryop"))
    return
    elt = add_node(parent, node, "row")
    op = add(elt, text=read_unaryop(node.op))
    value = render(elt, node.operand)
    return elt


def read_unaryop(op: ast.unaryop):
    if isinstance(op, ast.USub):
        return "-"
    elif isinstance(op, ast.UAdd):
        return "+"
    elif isinstance(op, ast.Not):
        return "not "
    elif isinstance(op, ast.Invert):
        return "~"
    else:
        raise NotImplementedError("unknown unary operator")





def read_boolop(op: ast.boolop):
    if isinstance(op, ast.And):
        return "and"
    elif isinstance(op, ast.Or):
        return "or"
    else:
        raise NotImplementedError(f"unknown boolean operator: {op}")


def render_ifexp(node: ast.IfExp):
    yield from element("bg-red", text("ifexp"))
    return
    elt = add_node(parent, node, "row gap")
    condition = add(elt)
    test = render(condition, node.test)

    if_part = add(elt, "if-prefix row gap")
    if_expr = render(if_part, node.body)
    else_part = add(elt, "else-prefix row gap")
    else_expr = render(else_part, node.orelse)
    return elt


# TODO: test with more kinds of literals
def render_dict(node: ast.Dict):
    yield from element("bg-red", text("dict"))
    return

    # TODO: multi-line rendering:
    # ... {
    #     ....
    # }
    # for now: render on a single line
    # TODO:
    elt = add_node(parent, node, "row braces")
    items = add(elt, "comma-sep")
    for i in range(len(node.keys)):
        k = node.keys[i]
        # TODO: None is for **d unpacking
        assert k is not None
        v = node.values[i]
        key = add(items, "row colon-suffix")
        expression.render(key)
        value = add(items)
        expression.render(value, v)


def render_list_comprehension(node: ast.ListComp):
    yield from element("bg-red", text("list_comprehension"))
    return
    elt = add_node(parent, node, "brackets row")
    spaced_content = add(elt, "row gap")
    selected = render(spaced_content, node.elt)
    # TODO: test with more than 1 generator
    generators = add(spaced_content, "row gap")
    for g in node.generators:
        expr = render_comprehension_generator(generators, g)
    return elt

def render_comprehension_generator(node: ast.comprehension):
    yield from element("bg-red", text("comprehension_generator"))
    return
    # TODO: support async
    assert node.is_async == 0

    elt = add_node(parent, node, "for-prefix row gap")
    # need a wrapper (row gap is the interaction with the in suffix) for in-sep
    generator = add(elt, "in-sep row gap")
    target = render(add(generator, "row gap"), node.target)
    it = render(add(generator, "row gap"), node.iter)

    conditions = add(elt, "row gap")
    for cond in node.ifs:
        condition = add(conditions, "if-prefix row gap")
        render(condition, cond)

    return elt


# TODO: implement

def render_yield(node):
    yield from element("bg-red", text("yield"))


def render_yieldfrom(node):
    yield from element("bg-red", text("yieldfrom"))


def render_compare(node: ast.Compare):
    yield from element("bg-red", text("compare"))
    return
    # in python, comparisons can be complex sequences, like:
    # 1 < x < y < 6
    # 1 is called left
    # the operators are [<, <, <]
    # and the comparators are [x, y, 6]
    elt = add_node(parent, node, "compare row gap")
    left = render(elt, node.left)
    for op, cmp in zip(node.ops, node.comparators):
        add(elt, text=read_op(op))
        render(elt, cmp)
    return elt

def read_op(op: ast.operator):
    if isinstance(op, ast.Eq):
        return "=="
    elif isinstance(op, ast.NotEq):
        return "!="
    elif isinstance(op, ast.Lt):
        return "<"
    elif isinstance(op, ast.LtE):
        return "<="
    elif isinstance(op, ast.Gt):
        return ">"
    elif isinstance(op, ast.GtE):
        return ">="
    elif isinstance(op, ast.Is):
        return "is"
    elif isinstance(op, ast.IsNot):
        return "is not"
    elif isinstance(op, ast.In):
        return "in"
    elif isinstance(op, ast.NotIn):
        return "not in"
    else:
        raise NotImplementedError("unknown comparison operator")




# TODO: add more DOM encoding
def render_call(node: ast.Call):
    yield from element("bg-red", text("call"))
    return
    elt = add_node(parent, node, "call row")
    func = render(elt, node.func)
    args = add(elt, "parens row")
    comma_separated = add(args, "comma-sep row")
    # positional args
    for arg in node.args:
        render(add(comma_separated, "row gap"), arg)
    # kwargs
    for kwarg in node.keywords:
        render_keyword_arg(add(comma_separated, "row gap"), kwarg)
        #eq_separated = add(comma_separated, "equal-sep row")
        #kw = add(eq_separated, text=kwarg.arg)
        #render(eq_separated, kwarg.value)
    return elt

# part of render_call(), also used by statement.render_class()
def render_keyword_arg(node: ast.keyword):
    yield from element("bg-red", text("keyword_arg"))
    return
    elt = add_node(parent, node, "equal-sep row")
    # TODO: use a wrapper for "row"
    # not needed here because there is only text,
    # but .equal-sep adds a ::before text content
    # and using a wrapper div would unify the DOM conventions with the rest of the code
    kw = add(elt, "row", text=node.arg)
    val = add(elt, "row")
    render(val, node.value)
    return elt

def render_formatted_value(node: ast.FormattedValue):
    yield from element("bg-red", text("formatted_value"))
    return
    # TODO: support other conversion types:
    # -1: unspecified (default is str())
    # 97: !a, ascii
    # 114: !r, repr() output
    # 115: !s, str() output
    assert node.conversion == -1
    # can be a nested JoinedStr instead of None
    # TODO: support this attribute
    assert node.format_spec is None
    elt = add_node(parent, node)
    render(elt, node.value)
    return elt


# f"{x}<text>{y}"
# f-"-({(<x>)}-(<json-encoded text>)-({<y>}))-"
def render_joinedstr(node: ast.JoinedStr):
    yield from element("bg-red", text("joinedstr"))
    return
    elt = add_node(parent, node, "row f-prefix")
    quoted = add(elt, "quotes row")
    for e in node.values:
        if isinstance(e, ast.FormattedValue):
            braced = add(quoted, "braces row")
            render(braced, e)
        else:
            assert isinstance(e, ast.Constant)
            assert isinstance(e.value, str)
            # quotes are replaced because pywebview runs f"elt.textContent = '{text}'"
            # which breaks if there is a single quote in the string
            # and needs a second layer of escaping for everything that is escaped
            # TODO: merge with literal string formatting
            str_text = json.dumps(e.value).replace("\\", "\\\\").replace("'", "\\'")
            # remove quotes (and let the css quotes surround the whole f-string)
            str_text = str_text[1:-1]
            #add(quoted, text=text)
            pre = add_pre(quoted, text=str_text)
            #parts.append(e.value)
    return elt


def render_constant(node: ast.Constant):
    yield from element("bg-red", text("constant"))
    return
    assert node.kind is None
    elt = add_node(parent, node, "literal")
    # TODO: test very carefully
    # string rendering is very fragile, due to pywebview doing a double eval with JS code execution
    # also make sure to check html escaping
    # and make sure that the code works in later versions with pypy
    # TODO: centralize string escaping to prevent debugging the same bugs in other places (f-strings, comparisons,...)

    # tools available:
    # -html.escape(), already done by pywebview
    # -json.dumps(), for JS quotes escaping (repr will not work)
    # -double escaping for the rest: .replace("\\", "\\\\")

    if isinstance(node.value, str):
        # TODO: use the DOM to encode constant types
        # TODO: render multiline ("\n") strings with the multiline syntax if they are top-level in the module

        # text = json.dumps(node.value)
        # pywebview uses JS eval to do things, which seems to break newline and quote escaping
        #text = json.dumps(node.value).replace("\\", "\\\\")
        # new fix imported from f-string (JoinedStr) tests
        str_text = json.dumps(node.value).replace("\\", "\\\\").replace("'", "\\'")
        elt.text = str_text
        # TODO: format multiline strings differently (""" """)
        # does not work:
        # (js eval replaces escaped "\n" by \n)
        #text = json.dumps(node.value).replace("'", "\\'")
        # remove quotes
        #text = text[1:-1]
        #if "\\n" in text:
        #    c = "triple-quotes"
        #else:
        #    c = "quotes"
        #pre = add_pre(elt, text)
        #pre.classes.append("bg-red")
        #elt.classes.append(c)
    else:
        elt.text = repr(node.value)
        #print(elt.text)
    return elt

def render_attribute(node: ast.Attribute):
    yield from element("bg-red", text("attribute"))
    return
    elt = add_node(parent, node, "attribute row dot-sep")
    render(elt, node.value)
    add(add(elt, "row"), text=node.attr)
    return elt

def render_subscript(node: ast.Subscript):
    yield from element("bg-red", text("subscript"))
    return
    # node.ctx is either ast.Load or ast.Store
    # Store if the subscript is in a left side of an assignment
    # Load if the subscript is in an expression to evaluate
    elt = add_node(parent, node, "row")
    indexed = render(elt, node.value)
    bracketed = add(elt, "brackets row")
    index = render(bracketed, node.slice)
    return elt


def render_starred(node: ast.Starred):
    yield from element("bg-red", text("starred"))
    return
    #print(node.ctx)
    elt = add_node(parent, node, "star-prefix row")
    render(elt, node.value)
    return elt

@register_node
def render_name(node: ast.Name):
    yield from element("symbol", text(node.id))

def render_list(node: ast.List):
    yield from element("bg-red", text("list"))
    return
    assert isinstance(node.ctx, ast.Load)
    elt = add_node(parent, node, "brackets row")
    comma_separated = add(elt, "comma-sep row")
    for x in node.elts:
        comma_ended = add(comma_separated, "row gap")
        render(comma_ended, x)
    return elt


def render_tuple(node: ast.Tuple):
    yield from element("bg-red", text("tuple"))
    return
    #print(node.ctx)
    elt = add_node(parent, node, "parens row")
    if len(node.elts) == 0:
        pass
    elif len(node.elts) == 1:
        # display a single item with a comma after it
        comma_separated = add(elt, "comma-sep row")
        render(add(comma_separated, "row"), node.elts[0])
        # empty element for the comma
        add(comma_separated)
    else:
        comma_separated = add(elt, "comma-sep row")
        for x in node.elts:
            render(add(comma_separated, "row gap"), x)
    return elt


def render_slice(node: ast.Slice):
    elt = add_node(parent, node)
    colon_split = add(elt, "row colon-sep")
    left = add(colon_split, "row")
    if node.lower is not None:
        render(left, node.lower)
    center = add(colon_split, "row")
    if node.upper is not None:
        render(center, node.upper)
    if node.step is not None:
        right = add(colon_split, "row")
        render(right, node.step)
    return elt

