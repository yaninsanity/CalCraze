import ast
import operator

# 允许的运算符映射
allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv
}

def safe_eval(expr: str) -> float:
    """
    使用 AST 安全解析表达式，只允许加、减、乘、除运算。
    """
    tree = ast.parse(expr, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        # Python 3.8+ 使用 ast.Constant 表示数字
        elif hasattr(ast, "Constant") and isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in allowed_operators:
                left = _eval(node.left)
                right = _eval(node.right)
                if op_type == ast.Div and right == 0:
                    raise ZeroDivisionError("Division by zero")
                return allowed_operators[op_type](left, right)
            else:
                raise ValueError("Unsupported operator")
        else:
            raise ValueError("Unsupported expression")
    return _eval(tree.body)
