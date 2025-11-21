"""
expression rendering
"""

from webview.dom.element import Element
import ast

import html
import json

from .dom import register, div, block, add_node, add, add_text, add_pre


def render(parent: Element, node: ast.expr):
    match type(node):
        case ast.BoolOp:
            return render_boolop(parent, node)
        case ast.NamedExpr:
            raise NotImplementedError('expression.render() not implemented for ast.NamedExpr')
        case ast.BinOp:
            return render_binop(parent, node)
        case ast.UnaryOp:
            return render_unaryop(parent, node)
        case ast.Lambda:
            raise NotImplementedError('expression.render() not implemented for ast.Lambda')
        case ast.IfExp:
            return render_ifexp(parent, node)
        case ast.Dict:
            raise NotImplementedError('expression.render() not implemented for ast.Dict')
        case ast.Set:
            raise NotImplementedError('expression.render() not implemented for ast.Set')
        case ast.ListComp:
            return render_list_comprehension(parent, node)
        case ast.SetComp:
            raise NotImplementedError('expression.render() not implemented for ast.SetComp')
        case ast.DictComp:
            raise NotImplementedError('expression.render() not implemented for ast.DictComp')
        case ast.GeneratorExp:
            raise NotImplementedError('expression.render() not implemented for ast.GeneratorExp')
        case ast.Await:
            raise NotImplementedError('expression.render() not implemented for ast.Await')
        case ast.Yield:
            raise NotImplementedError('expression.render() not implemented for ast.Yield')
        case ast.YieldFrom:
            raise NotImplementedError('expression.render() not implemented for ast.YieldFrom')
        case ast.Compare:
            return render_compare(parent, node)
        case ast.Call:
            return render_call(parent, node)
        case ast.FormattedValue:
            return render_formatted_value(parent, node)
        # case ast.Interpolation:
        #     raise NotImplementedError('expression.render() not implemented for ast.Interpolation')
        case ast.JoinedStr:
            return render_joinedstr(parent, node)
        # case ast.TemplateStr:
        #     raise NotImplementedError('expression.render() not implemented for ast.TemplateStr')
        case ast.Constant:
            return render_constant(parent, node)
        case ast.Attribute:
            return render_attribute(parent, node)
        case ast.Subscript:
            return render_subscript(parent, node)
        case ast.Starred:
            return render_starred(parent, node)
        case ast.Name:
            return render_name(parent, node)
        case ast.List:
            return render_list(parent, node)
        case ast.Tuple:
            return render_tuple(parent, node)
        case ast.Slice:
            raise NotImplementedError('expression.render() not implemented for ast.Slice')
        case default:
            raise ValueError(f"Unexpected ast expression type: {type(node)}")




#BoolOp(boolop op, expr* values)
#NamedExpr(expr target, expr value)
#BinOp(expr left, operator op, expr right)
#UnaryOp(unaryop op, expr operand)
#Lambda(arguments args, expr body)
#IfExp(expr test, expr body, expr orelse)
#Dict(expr?* keys, expr* values)
#Set(expr* elts)
#ListComp(expr elt, comprehension* generators)
#SetComp(expr elt, comprehension* generators)
#DictComp(expr key, expr value, comprehension* generators)
#GeneratorExp(expr elt, comprehension* generators)
## the grammar constrains where yield expressions can occur
#Await(expr value)
#Yield(expr? value)
#YieldFrom(expr value)
## need sequences for compare to distinguish between
## x < 4 < 3 and (x < 4) < 3
#Compare(expr left, cmpop* ops, expr* comparators)
#Call(expr func, expr* args, keyword* keywords)
#FormattedValue(expr value, int conversion, expr? format_spec)
#Interpolation(expr value, constant str, int conversion, expr? format_spec)
#JoinedStr(expr* values)
#TemplateStr(expr* values)
#Constant(constant value, string? kind)
#
## the following expression can appear in assignment context
#Attribute(expr value, identifier attr, expr_context ctx)
#Subscript(expr value, expr slice, expr_context ctx)
#Starred(expr value, expr_context ctx)
#Name(identifier id, expr_context ctx)
#List(expr* elts, expr_context ctx)
#Tuple(expr* elts, expr_context ctx)
#
#- can appear only in Subscript
#Slice(expr? lower, expr? upper, expr? step)
#
#

def render_boolop(parent: Element, node: ast.BoolOp) -> Element:
    elt = add_node(parent, node, "row gap")
    elt.classes.append(f"{read_boolop(node.op)}-sep")
    for v in node.values:
        # add(..., "row") is a wrapper required by the {op}-sep separator
        render(add(elt, "row gap"), v)
    return elt


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
def render_binop(parent: Element, node: ast.BinOp) -> Element:
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
    operator_suffixed.attributes["data-operator"] = read_binaryop(node.op)

    left = render(operator_suffixed, node.left)
    right = render(add(elt, "row gap"), node.right)
    return elt

def read_binaryop(op: ast.operator):
    # css classes cannot have special characters like +
    if isinstance(op, ast.Add):
        return "+"
    elif isinstance(op, ast.Sub):
        return "-"
    elif isinstance(op, ast.Mult):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.Div):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.FloorDiv):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.Mod):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.Pow):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.LShift):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.RShift):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.BitOr):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.BitXor):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.BitAnd):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    elif isinstance(op, ast.MatMult):
        raise NotImplementedError(f"unknown binary operator: {op}")
        pass
    raise NotImplementedError(f"unknown binary operator: {op}")


# TODO: go back to previous "operator separators" and replace them by DOM nodes
# (operators have semantic meaning, they are not just syntax)
# (keep the css for infix inlining if needed)
def render_unaryop(parent: Element, node: ast.UnaryOp) -> Element:
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


def render_ifexp(parent: Element, node: ast.IfExp) -> Element:
    elt = add_node(parent, node, "row gap")
    condition = add(elt)
    test = render(condition, node.test)

    if_part = add(elt, "if-prefix row gap")
    if_expr = render(if_part, node.body)
    else_part = add(elt, "else-prefix row gap")
    else_expr = render(else_part, node.orelse)
    return elt


def render_list_comprehension(parent: Element, node: ast.ListComp) -> Element:
    elt = add_node(parent, node, "brackets row")
    spaced_content = add(elt, "row gap")
    selected = render(spaced_content, node.elt)
    # TODO: test with more than 1 generator
    generators = add(spaced_content, "row gap")
    for g in node.generators:
        expr = render_comprehension_generator(generators, g)
    return elt

def render_comprehension_generator(parent: Element, node: ast.comprehension) -> Element:
    # TODO: support async
    assert node.is_async == 0
    # TODO: support conditions in comprehensions
    assert len(node.ifs) == 0

    elt = add_node(parent, node, "for-prefix in-sep row gap")
    # need a wrapper (row gap is the interaction with the in suffix) for in-sep
    target = render(add(elt, "row gap"), node.target)
    it = render(elt, node.iter)
    return elt


def render_compare(parent: Element, node: ast.Compare) -> Element:
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
def render_call(parent: Element, node: ast.Call) -> Element:
    elt = add_node(parent, node, "call row")
    func = render(elt, node.func)
    args = add(elt, "parens row")
    comma_separated = add(args, "comma-sep row")
    # positional args
    for arg in node.args:
        render(add(comma_separated, "row gap"), arg)
    # kwargs
    for kwarg in node.keywords:
        render_keyword_arg(add(comma_separated, "row"), kwarg)
        #eq_separated = add(comma_separated, "equal-sep row")
        #kw = add(eq_separated, text=kwarg.arg)
        #render(eq_separated, kwarg.value)
    return elt

# part of render_call(), also used by statement.render_class()
def render_keyword_arg(parent: Element, node: ast.keyword) -> Element:
    elt = add_node(parent, node, "equal-sep row")
    # TODO: use a wrapper for "row" ?
    # not needed here because there is only text,
    # but .equal-sep adds a ::before text content
    # and using a wrapper div would unify the DOM conventions with the rest of the code
    kw = add(elt, "row", text=node.arg)
    render(elt, node.value)
    return elt

def render_formatted_value(parent: Element, node: ast.FormattedValue) -> Element:
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
def render_joinedstr(parent: Element, node: ast.JoinedStr) -> Element:
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
            text = json.dumps(e.value).replace("\\", "\\\\").replace("'", "\\'")
            # remove quotes (and let the css quotes surround the whole f-string)
            text = text[1:-1]
            #add(quoted, text=text)
            pre = add_pre(quoted, text=text)
            #parts.append(e.value)
    return elt


def render_constant(parent: Element, node: ast.Constant) -> Element:
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
        text = json.dumps(node.value).replace("\\", "\\\\").replace("'", "\\'")
        elt.text = text
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

def render_attribute(parent: Element, node: ast.Attribute) -> Element:
    elt = add_node(parent, node, "attribute row dot-sep")
    render(add(elt, "row"), node.value)
    add(elt, text=node.attr)
    return elt

def render_subscript(parent: Element, node: ast.Subscript) -> Element:
    # node.ctx is either ast.Load or ast.Store
    # Store if the subscript is in a left side of an assignment
    # Load if the subscript is in an expression to evaluate
    elt = add_node(parent, node, "row")
    indexed = render(elt, node.value)
    bracketed = add(elt, "brackets row")
    index = render(bracketed, node.slice)
    return elt


def render_starred(parent: Element, node: ast.Starred) -> Element:
    #print(node.ctx)
    elt = add_node(parent, node, "star-prefix row")
    render(elt, node.value)
    return elt

def render_name(parent: Element, node: ast.Name) -> Element:
    elt = add_node(parent, node, "symbol")
    elt.text = node.id
    return elt

def render_list(parent: Element, node: ast.List) -> Element:
    assert isinstance(node.ctx, ast.Load)
    elt = add_node(parent, node, "brackets row")
    comma_separated = add(elt, "comma-sep row gap")
    for x in node.elts:
        comma_ended = add(comma_separated, "row")
        render(comma_ended, x)
    return elt


def render_tuple(parent: Element, node: ast.Tuple) -> Element:
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
        comma_separated = add(elt, "comma-sep row gap")
        for x in node.elts:
            render(add(comma_separated, "row"), x)
    return elt
