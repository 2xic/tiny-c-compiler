"""
All compilers have a optimizer

This one is very basic.
- Remove unused variables
- Constant fold expressions
- More ?
"""
from .ast import FunctionDefinition, MathOp, VariableDeclaration, Nodes, NumericValue

"""
TODO: THis should really run on some IR instead of the raw ast ...
"""
class Optimizer:
    def __init__(self) -> None:
        pass

    # Input is math op -> Output numeric value iff there is a way to constant fold.
    def process(self, function: FunctionDefinition):
        nodes = [
            function,
        ]
        while len(nodes):
            node = nodes.pop(0)
            if not isinstance(node, Nodes):
                continue
            if isinstance(node, VariableDeclaration):
                # pass
                if isinstance(node.value, MathOp):
                    node.value = self._constant_fold_math_op(node.value)            
            nodes += node.child_nodes

        return function

    def _constant_fold_math_op(self, node):
        values = []
        nodes = [node]
        while len(nodes):
            node = nodes.pop(0)
            if node.op == "+" and isinstance(node.expr_1, NumericValue) and isinstance(node.expr_2, NumericValue):
                values.append(str(int(node.expr_1.value) + int(node.expr_2.value)))
            else:
                # Not implemented, but idea is to explore the math op and evaluate it 
                return None
        return NumericValue(values[0])
