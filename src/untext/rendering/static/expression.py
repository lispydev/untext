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

import html as pyhtml
import json

#from untext.rendering.html import register, div, add_node, add, add_text, add_pre
from .html import text, element, debug, register_node, div
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


# part of render_boolop
def read_boolop(op: ast.boolop):
    if isinstance(op, ast.And):
        return "and"
    elif isinstance(op, ast.Or):
        return "or"
    else:
        raise NotImplementedError(f"unknown boolean operator: {op}")


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
@register_node
def render_binop(node: ast.BinOp):
    left = render(node.left)
    right = render(node.right)
    # TODO: find better abstractions
    # currently, using data attributes can only be done with div()
    right = div(right,
                classes="row gap",
                attr={"operator": read_binaryop(node.op)})

    result = element("operation row gap", left, right)
    yield from result


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
    value = render(node.operand)
    op = read_unaryop(node.op)
    yield from div(value,
                   classes="unary-operation row gap",
                   attr={"operator": op})


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


@register_node
def render_ifexp(node: ast.IfExp):
    test = render(node.test)

    if_expr = render(node.body)
    if_part = element("if-prefix row gap", if_expr)

    else_expr = render(node.orelse)
    else_part = element("else-prefix row gap", else_expr)

    if_expr = element("row gap", test, if_part, else_part)
    yield from element("if-expression", if_expr)


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


@register_node
def render_list_comprehension(node: ast.ListComp):
    # TODO: test with more than 1 generator
    generators = []
    for g in node.generators:
        generators.append(render_comprehension_generator(g))
    elt = render(node.elt)
    generators = element("row gap", *generators)
    content = element("row gap", elt, generators)
    yield from element("list-comprehension brackets row", content)


@register_node
def render_comprehension_generator(node: ast.comprehension):
    # TODO: support async
    assert node.is_async == 0

    conds = []
    for cond in node.ifs:
        cond = render(cond)
        conds.append(cond)
    conds = html.items("row gap", "if-prefix row gap", conds)

    target = render(node.target)
    iterated = render(node.iter)
    generator = html.items("in-sep row gap", "row gap", [target, iterated])
    yield from element("comprehension-generator for-prefix row gap", generator)



# TODO: implement

def render_yield(node):
    yield from element("bg-red", text("yield"))


def render_yieldfrom(node):
    yield from element("bg-red", text("yieldfrom"))


def render_compare(node: ast.Compare):
    # in python, comparisons can be complex sequences, like:
    # 1 < x < y < 6
    # 1 is called left
    # the operators are [<, <, <]
    # and the comparators are [x, y, 6]
    left = render(node.left)
    elts = [left]
    for op, cmp in zip(node.ops, node.comparators):
        op = text(read_op(op))
        cmp = render(cmp)
        elts.append(op)
        elts.append(cmp)
    yield from element("compare row gap", *elts)


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
@register_node
def render_call(node: ast.Call):
    func = render(node.func)
    args = [render(arg) for arg in node.args]
    kwargs = [render_keyword_arg(kwarg) for kwarg in node.keywords]
    args = html.items("comma-sep row", "row gap", args + kwargs)
    args = element("parens row", args)
    yield from element("call row", func, args)


# part of render_call(), also used by statement.render_class()
@register_node
def render_keyword_arg(node: ast.keyword):
    kw = text(node.arg)
    val = render(node.value)
    yield from html.items("keyword-argument equal-sep row", "row", [kw, val])


@register_node
def render_formatted_value(node: ast.FormattedValue):
    # TODO: support other conversion types:
    # -1: unspecified (default is str())
    # 97: !a, ascii
    # 114: !r, repr() output
    # 115: !s, str() output
    assert node.conversion == -1
    # can be a nested JoinedStr instead of None
    # TODO: support this attribute
    assert node.format_spec is None
    expr = render(node.value)
    yield from element("f-value", expr)


# f"{x}<text>{y}"
# f-"-({(<x>)}-(<json-encoded text>)-({<y>}))-"
# TODO: remove unneeded .string-literal classes
@register_node
def render_joinedstr(node: ast.JoinedStr):
    parts = []
    for e in node.values:
        if isinstance(e, ast.FormattedValue):
            e = render(e)
            braced = element("braces row", e)
            string_styled = element("string-literal", braced)
            parts.append(string_styled)
        else:
            assert isinstance(e, ast.Constant)
            assert isinstance(e.value, str)
            str_text = html_serialize_str(e.value)
            # remove quotes (and let the css quotes surround the whole f-string)
            # quotes are converted to "&quot;" by html_serialize_str
            str_text = str_text[6:-6]
            # TODO: see if string-literal is better for the whole f-string
            txt = text(str_text)
            txt = element("string-literal", txt)
            parts.append(txt)

    quoted = element("quotes row", *parts)
    string_styled = element("string-literal", quoted)
    yield from element("row f-prefix", string_styled)


@register_node
def render_constant(node: ast.Constant):
    assert node.kind is None

    if isinstance(node.value, str):
        # TODO: test with multiline strings,
        # make it work with the DOM renderer,
        # and refactor into a function
        str_text = html_serialize_str(node.value)
        txt = element("string-literal", text(str_text))
        const = div(txt, classes="literal", attr={"const-type": "str"})
    else:
        typename = type(node.value).__name__
        value_text = text(repr(node.value))
        const = div(value_text,
                  classes="literal",
                  attr={"const-type": typename})
    yield from element("constant", const)


# used by render_constant and render_joinedstr
def html_serialize_str(txt: str) -> str:
    return pyhtml.escape(json.dumps(txt))


@register_node
def render_attribute(node: ast.Attribute):
    obj = render(node.value)
    attr = text(node.attr)
    row = html.items("attribute row dot-sep", "row", [obj, attr])
    yield from row


@register_node
def render_subscript(node: ast.Subscript):
    # node.ctx is either ast.Load or ast.Store
    # Store if the subscript is in a left side of an assignment
    # Load if the subscript is in an expression to evaluate
    index = render(node.slice)
    bracketed = element("brackets row", index)
    indexed = render(node.value)
    yield from element("subscript row", indexed, bracketed)


@register_node
def render_starred(node: ast.Starred):
    expr = render(node.value)
    yield from element("starred star-prefix row", expr)


@register_node
def render_name(node: ast.Name):
    yield from element("symbol", text(node.id))


@register_node
def render_list(node: ast.List):
    assert isinstance(node.ctx, ast.Load)
    elts = [render(x) for x in node.elts]
    elts = html.items("comma-sep row", "row gap", elts)
    yield from element("list brackets row", elts)


@register_node
def render_tuple(node: ast.Tuple):
    #print(node.ctx)
    # TODO: cleanup this branching
    if len(node.elts) == 0:
        yield from element("tuple parens row")
        return
    if len(node.elts) == 1:
        # display a single item with a comma after it
        expr = render(node.elts[0])
        # empty element for the comma
        empty_elt = element()
        comma_separated = html.items("comma-sep row", "row", [expr, empty_elt])
        yield from element("tuple parens row", comma_separated)
        return
    else:
        elts = [render(e) for e in node.elts]
        elts = html.items("comma-sep row", "row gap", elts)
        yield from element("tuple parens row", elts)
        return


@register_node
def render_slice(node: ast.Slice):
    # a slice must have a left and right part separated by :, even if they are implicit
    parts = [element("optional-slot"), element("optional-slot")]
    if node.lower is not None:
        parts[0] = render(node.lower)
    if node.upper is not None:
        parts[1] = render(node.upper)
    if node.step is not None:
        parts.append(render(node.step))
    yield from html.items("slice row colon-sep", "row", parts)

