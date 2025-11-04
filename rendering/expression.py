"""
expression rendering
"""

from webview.dom.element import Element
import ast

import html
import json

from .dom import register, div, block, add_node, add, add_text

def render(parent: Element, node: ast.expr):
    match type(node):
        case ast.BoolOp:
            raise NotImplementedError('expression.render() not implemented for ast.BoolOp')
        case ast.NamedExpr:
            raise NotImplementedError('expression.render() not implemented for ast.NamedExpr')
        case ast.BinOp:
            raise NotImplementedError('expression.render() not implemented for ast.BinOp')
        case ast.UnaryOp:
            raise NotImplementedError('expression.render() not implemented for ast.UnaryOp')
        case ast.Lambda:
            raise NotImplementedError('expression.render() not implemented for ast.Lambda')
        case ast.IfExp:
            raise NotImplementedError('expression.render() not implemented for ast.IfExp')
        case ast.Dict:
            raise NotImplementedError('expression.render() not implemented for ast.Dict')
        case ast.Set:
            raise NotImplementedError('expression.render() not implemented for ast.Set')
        case ast.ListComp:
            raise NotImplementedError('expression.render() not implemented for ast.ListComp')
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
            raise NotImplementedError('expression.render() not implemented for ast.Compare')
        case ast.Call:
            raise NotImplementedError('expression.render() not implemented for ast.Call')
        case ast.FormattedValue:
            raise NotImplementedError('expression.render() not implemented for ast.FormattedValue')
        # case ast.Interpolation:
        #     raise NotImplementedError('expression.render() not implemented for ast.Interpolation')
        case ast.JoinedStr:
            raise NotImplementedError('expression.render() not implemented for ast.JoinedStr')
        # case ast.TemplateStr:
        #     raise NotImplementedError('expression.render() not implemented for ast.TemplateStr')
        case ast.Constant:
            render_constant(parent, node)
        case ast.Attribute:
            raise NotImplementedError('expression.render() not implemented for ast.Attribute')
        case ast.Subscript:
            raise NotImplementedError('expression.render() not implemented for ast.Subscript')
        case ast.Starred:
            raise NotImplementedError('expression.render() not implemented for ast.Starred')
        case ast.Name:
            render_name(parent, node)
        case ast.List:
            raise NotImplementedError('expression.render() not implemented for ast.List')
        case ast.Tuple:
            raise NotImplementedError('expression.render() not implemented for ast.Tuple')
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


def render_constant(parent: Element, node: ast.Constant):
    assert node.kind is None
    elt = add_node(parent, node)
    # TODO: test carefully
    # there could be other places where html can get by mistake
    # html.escape() means we can't have html in the string literals of the edited source code
    if isinstance(node.value, str):
        # TODO: use the DOM to encode constant types
        # TODO: render multiline ("\n") strings with the multiline syntax if they are top-level in the module
        text = json.dumps(html.escape(node.value))
        print(text)
        # this line will use auto-generated js to set the text, and it seems pywebview forgot character escaping
        #elt.text = text.replace("\\", "")
        elt.text = text
        print(elt.text)
    else:
        elt.text = repr(node.value)
        print(elt.text)

def render_name(parent: Element, node: ast.Name):
    elt = add_node(parent, node)
    elt.text = node.id
    pass
