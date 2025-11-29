"""
This is the source code of the IDE you are running.

TODO: refactor html generation
TODO: write helpers for body generation
"""

# TODO: write tests
#print(1 < 3 < 5)

import webview
import html
import ast
import sys
import code
import os

# used to load css files in the python import path
from importlib import resources

#import multiprocessing
#import marshal
# force=True: do it even in the child process (otherwise, a RuntimeError is raised)
#multiprocessing.set_start_method("spawn", force=True)

#def run_code(encoded_bytecode, module_dict):
#    bytecode = marshal.loads(encoded_bytecode)
#    exec(bytecode, module_dict)



from types import ModuleType

# test import, needed for exhaustiveness of the renderer (TODO: remove once we have automated regression tests for the renderer)
import untext.rendering.dynamic.statement as statement, untext.rendering.dynamic.expression as expression
def f(a, b):
    pass

from untext.rendering.dynamic import dom
from untext.rendering.dynamic.dom import div_old as div, block

#import rendering.statement, rendering.expression

from untext.rendering.dynamic import statement, expression


from untext.rendering import static



"""
helpers to create DOM from an AST
"""
def render_module(module_node):
    # unknown value
    assert len(module_node.type_ignores) == 0
    children = ["<div>"]
    for elt in module_node.body:
        # top-level strings are usually multiline
        # TODO: refactor to make the logic more explicit
        if isinstance(elt, ast.Expr) and isinstance(elt.value, ast.Constant) and isinstance(elt.value.value, str):
            lines = elt.value.value.split("\n")
            lines[0] = '"""' + lines[0]
            lines[-1] += '"""'
            lines = [line if line else "<br>" for line in lines]
            lines = [f"<div>{line}</div>" for line in lines]
            children.append("".join(lines))
            # failed implementation
            #rendered_text = elt.value.value.replace("\n", "</div><div>")
            #print(rendered_text)
            #print("\n" in rendered_text)
            #children.append(f'<div>"""</div><div>{elt.value.value}</div><div>"""</div>')
        else:
            children.append(render_statement(elt))
    children.append("</div>")
    return "".join(children)


def render_statement(node):
    if isinstance(node, ast.Import):
        return render_import(node)
    elif isinstance(node, ast.ImportFrom):
        return render_importfrom(node)
    elif isinstance(node, ast.FunctionDef):
        return render_funcdef(node)
    elif isinstance(node, ast.Expr):
        return render_expr_statement(node)
    elif isinstance(node, ast.With):
        return render_with(node)
    elif isinstance(node, ast.Assign):
        return render_assign(node)
    elif isinstance(node, ast.While):
        return render_while(node)
    elif isinstance(node, ast.For):
        return render_for(node)
    elif isinstance(node, ast.Assert):
        return render_assert(node)
    elif isinstance(node, ast.Return):
        return render_return(node)
    elif isinstance(node, ast.If):
        return render_if(node)
    elif isinstance(node, ast.Pass):
        return render_pass(node)
    elif isinstance(node, ast.Try):
        return render_try(node)
    elif isinstance(node, ast.Raise):
        return render_raise(node)
    elif isinstance(node, ast.AugAssign):
        targ = render_expr(node.target)
        op = render_binaryop(node.op)
        val = render_expr(node.value)
        return f"{targ} {op}= {val}"
    elif isinstance(node, ast.ClassDef):
        # TODO:
        return ""
    elif isinstance(node, ast.Nonlocal):
        # TODO:
        return ""
    elif isinstance(node, ast.Match):
        # TODO:
        return ""
    elif isinstance(node, ast.Delete):
        # TODO:
        return ""
    else:
        raise NotImplementedError(type(node))


def render_import(import_node):
    # TODO: support more than 1 import per statement
    # use case: import (... as ..., ... as ...)
    #assert len(import_node.names) == 1
    #for alias in import_node.names:
    alias = import_node.names[0]
    if alias.asname is not None:
        return div(f"import {alias.name} as {alias.asname}")
    else:
        return div(f"import {alias.name}")

def render_importfrom(node):
    fragments = []
    for alias in node.names:
        if alias.asname is None:
            fragments.append(f"{alias.name}")
        else:
            fragments.append(f"{alias.name} as {alias.asname}")
    # TODO: support multiline syntax if the fragments are too long
    fragments = ", ".join(fragments)
    line = f"from {node.level * '.'}{node.module if node.module is not None else ''} import {fragments}"
    return div(line)



def render_funcdef(funcdef_node):
    n = funcdef_node
    body = []
    # type_params is a 3.12+ feature
    # TODO: use type_comment, wait for pypy to reach 3.12 or stop supporting pypy
    #assert len(n.type_params) == 0
    header = f"def {n.name}({render_arguments(n.args)}):"
    for statement in n.body:
        body.append(render_statement(statement))
    # TODO: support decorators in function definitions
    assert len(n.decorator_list) == 0
    # never seen otherwise yet
    # TODO: (done in the dynamic renderer)
    if n.returns is not None:
        pass
    assert n.type_comment is None

    header = div(header)
    body = "".join(body)
    body = block(body)
    return div(header + body)

def render_with(node):
    body = "".join([render_statement(statement) for statement in node.body])
    items = ", ".join([render_withitem(item) for item in node.items])
    assert node.type_comment is None
    header = div(f"with {items}:")
    body = block(body)
    result = div(header + body)
    return result

def render_withitem(node):
    expr = render_expr(node.context_expr)
    if node.optional_vars:
        name = render_expr(node.optional_vars)
        return f"{expr} as {name}"
    else:
        return expr


def render_assign(assign_node):
    targets = tuple([render_expr(t) for t in assign_node.targets])
    value = render_expr(assign_node.value)
    assert assign_node.type_comment is None
    if len(targets) == 1:
        target = targets[0]
        return div(f"{target} = {value}")
    else:
        return div(f"{tuple(targets)} = {value}")

def render_while(node):
    test = render_expr(node.test)
    body = [render_statement(statement) for statement in node.body]
    else_body = [render_statement(statement) for statement in node.orelse]
    header = div(f"while {test}:")
    body = "".join(body)
    body = block(body)
    return div(header + body)
def render_for(node):
    target = render_expr(node.target)
    it = render_expr(node.iter)
    header = div(f"for {target} in {it}:")
    body = [render_statement(statement) for statement in node.body]
    body = dom.block("".join(body))

    block = div(header + body)

    parts = [block]

    if node.orelse:
        else_header = div("else:")
        else_body = [render_statement(statement) for statement in node.orelse]
        else_body = block("".join(else_body))
        else_block = div(else_header + else_body)
        parts.append(else_block)

    assert node.type_comment is None

    result = "".join(parts)
    return div(result)


def render_assert(node):
    # TODO: support assertion messages
    assert node.msg is None
    test = render_expr(node.test)
    return div(f"assert {test}")
def render_return(node):
    if node.value is not None:
        result = render_expr(node.value)
        return div(f"return {result}")
    else:
        return ""
def render_if(node):
    # manual processing
    # the Python AST represent elif branches as nested else: if
    if is_elif(node):
        #print("found elif")
        return render_elifs(node)
    test = render_expr(node.test)
    body = [render_statement(s) for s in node.body]

    if_header = div(f"if {test}:")
    body = block("".join(body))

    ifpart = div(if_header + body)

    parts = [ifpart]

    if node.orelse:
        else_header = f"<div>else:</div>"
        else_body = [render_statement(s) for s in node.orelse]
        else_body = "".join(else_body)
        else_body = f"<div style='margin-left: 30px'>{else_body}</div>"

        elsepart = f"<div>{else_header}{else_body}</div>"
        parts.append(elsepart)
    return "".join(parts)

# helpers for elifs
def is_elif(if_node):
    "return True if the if has an elif branch"
    # if/elif gets compiled to if/else{if}
    # if/elif/else gets compiled to if/else{if/else}
    if len(if_node.orelse) != 1:
        return False
    return isinstance(if_node.orelse[0], ast.If)

def elif_depth(if_node):
    "return the number of elif branches in an if"
    n = 0
    while is_elif(if_node):
        n += 1
        if_node = if_node.orelse[0]
    return n

def collect_branches(if_node):
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

def render_elifs(if_node):
    branches = collect_branches(if_node)
    if_branch, *elif_branches, else_body = branches


    # if
    if_test, if_body = if_branch
    if_test = render_expr(if_test)
    if_header = f"<div>if {if_test}:</div>"

    if_body = [render_statement(s) for s in if_body]
    if_body = "".join(if_body)
    if_body = f"<div style='margin-left: 30px'>{if_body}</div>"

    ifpart = f"<div>{if_header}{if_body}</div>"

    parts = [ifpart]

    # elifs
    for (test, body) in elif_branches:
        test = render_expr(test)
        header = f"<div>elif {test}:</div>"
        body = [render_statement(s) for s in body]
        body = "".join(body)
        body = f"<div style='margin-left: 30px'>{body}</div>"
        part = f"<div>{header}{body}</div>"
        parts.append(part)

    # else
    if else_body:
        else_header = f"<div>else:</div>"
        else_body = [render_statement(s) for s in else_body]
        else_body = "".join(else_body)
        else_body = f"<div style='margin-left: 30px'>{else_body}</div>"
        elsepart = f"<div>{else_header}{else_body}</div>"
        parts.append(elsepart)

    return "".join(parts)
    #return ifpart



def render_pass(node):
    return "<div>pass</div>"
def render_try(node):
    body = [render_statement(statement) for statement in node.body]
    handlers = [render_except_handler(h) for h in node.handlers]
    header = f"<div>try:</div>"

    body = "".join(body)
    body = f"<div style='margin-left: 30px'>{body}</div>"

    parts = [header, body]

    for h in handlers:
        parts.append(h)

    if node.orelse:
        header = "<div>else:</div>"
        else_body = [render_statement(statement) for statement in node.orelse]
        else_body = "".join(else_body)
        else_body = f"<div style='margin-left: 30px'>{else_body}</div>"
        else_block = f"<div>{header}{else_body}</div>"
        parts.append(else_block)

    if node.finalbody:
        header = "<div>finally:</div>"
        final_body = [render_statement(statement) for statement in node.finalbody]
        final_body = "".join(final_body)
        final_body = f"<div style='margin-left: 30px'>{final_body}</div>"
        final_block = f"<div>{header}{final_body}</div>"
        parts.append(final_block)
    result = "".join(parts)
    return f"<div>{result}</div>"

def render_except_handler(node):
    error_type = render_expr(node.type)
    body = [render_statement(statement) for statement in node.body]
    header = f"<div>except {error_type} as {node.name}:</div>"
    body = "".join(body)
    body = f"<div style='margin-left: 30px'>{body}</div>"
    return f"<div>{header}{body}</div>"

def render_arguments(node):
    result = ", ".join([render_arg(arg) for arg in node.args])
    # TODO: support more cases
    assert len(node.posonlyargs) == 0
    assert len(node.kwonlyargs) == 0
    assert len(node.kw_defaults) == 0
    # TODO: implement in the static renderer (implemented in the dynamic renderer)
    if len(node.defaults) != 0:
        pass
    # flags (*args and **kwargs)
    # TODO: support this instead of ignoring it
    #assert node.vararg is None
    assert node.kwarg is None
    return result
def render_arg(arg):
    # TODO: support argument type annotations (implemented in the dynamic renderer)
    if arg.annotation is not None:
        pass
    assert arg.type_comment is None
    # text metadata (not needed in a no-text IDE)
    #print(arg.lineno)
    #print(arg.col_offset)
    #print(arg.end_lineno)
    #print(arg.end_col_offset)
    return arg.arg

def render_raise(node):
    # TODO: check if support is needed
    assert node.cause is None
    exc = render_expr(node.exc)
    return f"<div>raise {exc}</div>"


def render_expr_statement(node):
    return f"<div>{render_expr(node)}</div>"


"""
expression rendering
"""

def render_cmpop(node):
    if isinstance(node, ast.Eq):
        return "=="
    elif isinstance(node, ast.NotEq):
        return "!="
    elif isinstance(node, ast.Lt):
        return html.escape("<")
    elif isinstance(node, ast.LtE):
        return html.escape("<=")
    elif isinstance(node, ast.Gt):
        return html.escape(">")
    elif isinstance(node, ast.GtE):
        return html.escape(">=")
    elif isinstance(node, ast.Is):
        return "is"
    elif isinstance(node, ast.IsNot):
        return "is not"
    elif isinstance(node, ast.In):
        return "in"
    elif isinstance(node, ast.NotIn):
        return "not in"
    else:
        raise NotImplementedError("unknown comparison operator")


def render_unaryop(op):
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


def render_binaryop(op):
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
        pass
    elif isinstance(op, ast.BitXor):
        pass
    elif isinstance(op, ast.BitAnd):
        pass
    elif isinstance(op, ast.MatMult):
        pass
    raise NotImplementedError(f"unknown binary operator: {op}")

def render_boolop(op):
    if isinstance(op, ast.And):
        return "and"
    elif isinstance(op, ast.Or):
        return "or"
    else:
        raise NotImplementedError(f"unknown boolean operator: {op}")


def render_keyword(node):
    value = render_expr(node.value)
    return f"{node.arg}={value}"

def render_expr(node):
    if isinstance(node, ast.Expr):
        # nested Expr wrapper
        return render_expr(node.value)
    elif isinstance(node, ast.BoolOp):
        op = render_boolop(node.op)
        values = [render_expr(v) for v in node.values]
        result = f" {op} ".join(values)
        return result
    #elif isinstance(node, ast.NamedExpr):
    #    return "<span style='color: red'>TODO</span> named"
    elif isinstance(node, ast.BinOp):
        left = render_expr(node.left)
        op = render_binaryop(node.op)
        right = render_expr(node.right)
        return f"{left} {op} {right}"
    elif isinstance(node, ast.UnaryOp):
        op = render_unaryop(node.op)
        value = render_expr(node.operand)
        return f"{op}{value}"
    #elif isinstance(node, ast.Lambda):
    #    return "<span style='color: red'>TODO</span> "
    elif isinstance(node, ast.IfExp):
        test = render_expr(node.test)
        if_expr = render_expr(node.body)
        else_expr = render_expr(node.orelse)
        return f"{if_expr} if {test} else {else_expr}"
    elif isinstance(node, ast.Dict):
        return "<span style='color: red'>TODO</span> "
    #elif isinstance(node, ast.Set):
    #    return "<span style='color: red'>TODO</span> "
    elif isinstance(node, ast.ListComp):
        expr = render_expr(node.elt)
        generators = [render_comprehension(g) for g in node.generators]
        generators = [f"for {g}" for g in generators]
        # TODO: test with more than 1 generator
        generators = " ".join(generators)
        return f"[{expr} {generators}]"
    #elif isinstance(node, ast.SetComp):
    #    return "<span style='color: red'>TODO</span> "
    #elif isinstance(node, ast.DictComp):
    #    return "<span style='color: red'>TODO</span> "
    #elif isinstance(node, ast.GeneratorExp):
    #    return "<span style='color: red'>TODO</span> "
    #elif isinstance(node, ast.Await):
    #    return "<span  style='color: red'>TODO</span> "
    #elif isinstance(node, ast.Yield):
    #    return "<span style='color: red'>TODO</span> "
    #elif isinstance(node, ast.YieldFrom):
    #    return "<span style='color: red'>TODO</span> "
    elif isinstance(node, ast.Compare):
        # in python, comparisons can be complex sequences, like:
        # 1 < x < y < 6
        # 1 is called left
        # the operators are [<, <, <]
        # and the comparators are [x, y, 6]
        left = render_expr(node.left)
        operators = [render_cmpop(op) for op in node.ops]
        comparators = [render_expr(cmp) for cmp in node.comparators]
        items = [left]
        for op, cmp in zip(operators, comparators):
            items.append(op)
            items.append(cmp)
        return " ".join(items)
    elif isinstance(node, ast.Call):
        # positional args
        args = [render_expr(arg) for arg in node.args]
        # kwargs
        args.extend([render_keyword(kw) for kw in node.keywords])
        args = ", ".join(args)
        func = render_expr(node.func)
        return f"{func}({args})"
    elif isinstance(node, ast.FormattedValue):
        # TODO: support other values
        # 97: !a, ascii
        # 114: !r, repr() formatting
        # 115: !s, string formatting
        assert node.conversion == -1
        # nested JoinedStr or None
        assert node.format_spec is None
        return render_expr(node.value)
    #elif isinstance(node, ast.Interpolation):
    #    return "<span style='color: red'>TODO</span> "
    elif isinstance(node, ast.JoinedStr):
        parts = []
        for e in node.values:
            if isinstance(e, ast.FormattedValue):
                parts.append("{" + render_expr(e) + "}")
            else:
                # skip render_expr to avoid representing substrings with quotes
                assert isinstance(e, ast.Constant)
                assert isinstance(e.value, str)
                parts.append(e.value)
        string_result = "".join(parts)
        return html.escape(repr(string_result))
    #elif isinstance(node, ast.TemplateStr):
    #    return "<span style='color: red'>TODO</span> "
    elif isinstance(node, ast.Constant):
        assert node.kind is None
        # TODO: test carefully
        # there could be other places where html can get by mistake
        # html.escape() means we can't have html in the string literals of the edited source code
        if isinstance(node.value, str):
            return repr(html.escape(node.value))
        else:
            return repr(node.value)
    elif isinstance(node, ast.Attribute):
        obj = render_expr(node.value)
        attr = node.attr
        #print(node.ctx)
        #assert isinstance(node.ctx, ast.Load)
        return f"{obj}.{attr}"
    elif isinstance(node, ast.Subscript):
        indexed = render_expr(node.value)
        index = render_expr(node.slice)
        # node.ctx is either ast.Load or ast.Store
        # Store if the subscript is in a left side of an assignment
        # Load if the subscript is in an expression to evaluate
        return f"{indexed}[{index}]"
    elif isinstance(node, ast.Starred):
        #print(node.ctx)
        expr = render_expr(node.value)
        return f"*{expr}"
    elif isinstance(node, ast.Name):
        # the context can be Store (variable to store in, in assignment), Load (value to load), or Del (in del statements)
        # never used here for now
        #assert isinstance(node.ctx, ast.Store)
        return node.id
    elif isinstance(node, ast.List):
        elts = [render_expr(expr) for expr in node.elts]
        assert isinstance(node.ctx, ast.Load)
        elts = ", ".join(elts)
        return f"[{elts}]"
    elif isinstance(node, ast.Tuple):
        #print(node.ctx)
        elts = [render_expr(elt) for elt in node.elts]
        if len(elts) == 0:
            return "(,)"
        if len(elts) == 1:
            return f"({elts[0]},)"
        elts = ", ".join(elts)
        return f"({elts})"
    elif isinstance(node, ast.Slice):
        return "<span style='color: red'>TODO</span> "
    else:
        raise NotImplementedError(type(node))

def render_comprehension(node):
    target = render_expr(node.target)
    it = render_expr(node.iter)
    # TODO: support async
    assert node.is_async == 0
    # TODO: support conditions in comprehensions
    # TODO: implement in the dynamic renderer for now
    if len(node.ifs) > 0:
        pass
    #assert len(node.ifs) == 0
    #ifs = [render_expr(x) for x in node.ifs]
    #print(ifs)
    return f"{target} in {it}"



class Project:
    def __init__(self, project_root):
        self.path = os.path.abspath(project_root)

        self.windows = []

    # TODO: (someday) remove the load parameter and CodeWindow.load ?
    def open(self, filepath, load=True):
        # parse and check the file path
        absolute_path = os.path.abspath(filepath)
        common_part = os.path.commonpath([self.path, absolute_path])
        # TODO: improve error handling (user input)
        if common_part != self.path:
            raise ValueError(f"Cannot open {filepath}, as the file is not in the {self.path} project directory")
        assert absolute_path.startswith(common_part)
        relative_path = os.path.relpath(absolute_path, self.path) #absolute_path[len(common_part):]
        path_parts = os.path.normpath(relative_path).split(os.sep)
        module_name, ext = os.path.splitext(path_parts[-1])
        # TODO: improve error handling (user input)
        if ext != ".py":
            raise ValueError(f"Cannot open {filepath}, as the file is not a python script")
        path_parts[-1] = module_name

        self.windows.append(CodeWindow(self, path_parts, load=load))




class CodeWindow:
    def __init__(self, project, path_parts, load=True):
        self.project = project
        self.parent_packages = path_parts[:-1]
        self.filename = path_parts[-1]
        self.path = "/".join(path_parts)
        with open(f"{self.path}.py") as f:
            self.source = f.read()
        self.module_path = ".".join(path_parts)
        self.loaded = False
        self.module = None
        
        # create namespaces and packages to allow non-root imports without
        # requiring actual directories on disk:
        # (actually not needed, days of wasted research)

        # prepare packages for each step of the path to the current module
        #if len(path_parts) > 1:
        #    for i in range(len(path_parts) - 1):
        #        parts = path_parts[0:i + 1]
        #        pkg_path = ".".join(parts)
        #        #print(parts)
        #        if pkg_path in sys.modules:
        #            #print(pkg_path, "found in sys.modules")
        #            pass
        #        else:
        #            pkg = ModuleType(pkg_path)
        #            fs_path = os.path.abspath("/".join(parts))
        #            pkg.__path__ = [fs_path]
        #            # TODO: make the package a namespace if there is no __init__.py anywhere in the python path
        #            # else, find what to do when there are more than one __init__.py package with the same name
        #            # (preparing for these situations before they happen is better than debugging weird niche cases)

        #            # TODO: see in personal notes how to completely fake a namespace (need to test for unneeded steps, but will work in python3.13)

        #            #spec = ModuleSpec(
        #            #    name=pkg_path,
        #            #    loader=None,
        #            #    is_package=True,
        #            #)
        #            #spec.submodule_search_locations = [fs_path]
        #            #pkg.__spec__ = spec
        #            #pkg.__file__ = None
        #            #pkg.__loader__ = None
        #            # TODO: see if namespaces are actually useful or not
        #            sys.modules[pkg_path] = pkg
        #            print("created package", pkg_path, "at", fs_path)
        #            print(pkg)
        ##sys.modules[self.module_path] = self.module

        # TODO: update the static renderer and skip the initial DOM rendering
        self.tree = ast.parse(self.source)
        self.html = "".join(static.statement.render_module(self.tree)) #render_module(self.tree)

        # the API cannot have a CodeWindow as an attribute
        # the constructor cannot have parameters
        # closures are the only way to store self as the context of the API
        # so this class has to be defined here
        class CodeWindowAPI:
            js_init = """
            document.body.addEventListener("keydown", (e) => {
            pywebview.api.keydown(e.key)
            })
            """

            def keydown(_, key):
                if key == "r":
                    if not self.loaded:
                        if self.module_path in sys.modules:
                            self.module = sys.modules[self.module_path]
                        else:
                            self.module = ModuleType(self.module_path)
                        self.loaded = True
                    bytecode = compile(self.tree, "<ast>", "exec")
                    exec(bytecode, self.module.__dict__)
                    sys.modules[self.module_path] = self.module
                    # multiprocessing attempt
                    # breaks too much to be useful,
                    # even if some codes like pywebview only work in the main thread
                    #def f():
                    #    print(os.getpid())
                    #    print(os.getppid())
                    #    exec(bytecode, self.module.__dict__)
                    #encoded = marshal.dumps(bytecode)
                    #p = multiprocessing.Process(target=run_code, args=(encoded, self.module.__dict__))
                    #p.start()
                    #p.join()
                    #exec(bytecode, self.module.__dict__)
                elif key == "s":
                    self.refresh_module()
                    # start an REPL in the current module
                    code.InteractiveConsole(locals=self.module.__dict__).interact()
                print(key)

        self.api = CodeWindowAPI()
        self.window = webview.create_window(self.module_path, html=self.html, js_api=self.api)

        if load:
            self.load()


    # if the module was already imported in other places,
    # but never reloaded by the user,
    # pull the sys.modules entry and use it as the module
    def refresh_module(self):
        if not self.loaded and self.module_path in sys.modules:
            self.module = sys.modules[self.module_path]
            self.loaded = True


    # must be called after webview.start()
    # (load_css, evaluate_js and dom manipulation cannot be done before opening the window)
    def load(self):
        # inject css into the window and load the html
        for name in ["style.css", "syntax.css"]:
            # css files must be searched in the
            # python path with importlib,
            # since they are bundled and installed with pip
            css = resources.files("untext.css").joinpath(name).read_text()
            self.window.load_css(css)
        self.window.evaluate_js(self.api.js_init)
        self.root = self.window.dom.create_element("<div id='root'></div>")
        # will fail until the new renderer is complete
        statement.render_module(self.root, self.tree)


def main():
    # open files listed in sys.argv
    main_project = Project(os.getcwd())
    for path in sys.argv[1:]:
        if not os.path.exists(path):
            # create the file only if it doesn't exist
            with open(path, "x"):
                pass
        main_project.open(path, load=False)

    def on_load():
        # TODO: get rid of this step by starting pywebview before opening CodeWindows (with a ProjectWindow for example) or by using the static renderer first
        for win in main_project.windows:
            win.load()

    if not main_project.windows:
        print("Usage: untext <file1> <file2>")
        sys.exit(0)

    print("starting")
    webview.start(on_load)


if __name__ == "__main__":
    main()

