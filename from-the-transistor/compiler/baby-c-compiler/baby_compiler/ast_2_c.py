"""
You need to be able to go from AST back to C so we are sure our AST is of high quality.
"""
from .ast import Nodes, FunctionDefinition, FunctionBody, File, VariableDeclaration, MathOp, NumericValue, ReturnDefinition, VariableReference, TypeDefinition

class Ast2C:
    def __init__(self, ast: File) -> None:
        self.ast = ast

    def get_source_code(self):
        source_code = ""
        # ast = file
        for i in self.ast.functions:
            source_code += self._get_node_code(self.ast.functions[i])
        return source_code
    
    def _get_node_code(self, node: Nodes):
        if isinstance(node, FunctionDefinition):
            body = self._get_node_code(node.body) 
            return_argument = self._get_node_code(node.return_parameters)
            output = [
                return_argument,
                node.name,
                "()", # hardcoded for now,
                "{"
            ]
            function_def = [
                " ".join(output),
                body,
                "}"
            ]
            return "\n".join(function_def)
        elif isinstance(node, FunctionBody):
            output = []
            for i in node.child_nodes:
                output.append(self._get_node_code(i))
            return "\n".join(output)
        elif isinstance(node, VariableDeclaration):
            type_name = self._get_node_code(node.type)
            value = self._get_node_code(node.value)
            return f"{type_name} {node.name} = {value};"
        elif isinstance(node, MathOp):
            val_1 = self._get_node_code(node.expr_1)
            val_2 = self._get_node_code(node.expr_2)
            return f"{val_1} {node.op} {val_2}"
        elif isinstance(node, NumericValue):
            return node.value
        elif isinstance(node, ReturnDefinition):
            value = self._get_node_code(node.value)
            return f"return {value};"
        elif isinstance(node, VariableReference):
            return node.variable    
        elif isinstance(node, TypeDefinition):
            return node.name
        else:
            raise Exception("Unknown node " + str(node) + " " + node.__class__.__name__)
