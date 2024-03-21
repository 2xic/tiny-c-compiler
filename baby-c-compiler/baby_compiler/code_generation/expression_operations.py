from ..ast import NumericValue, VariableReference
from .asm_output_stream import AsmOutputStream
from .variable_operations import VariableLocation

class ExpressionOperations:
    def __init__(self, ast, parameter_location) -> None:
        self.ast = ast
        self.parameter_location = parameter_location

    def get_expression_load(self, node, output: AsmOutputStream):
        if isinstance(node, NumericValue):
            return f"${node.value}"
        elif isinstance(node, VariableReference):
            reference_stack = VariableLocation.from_variable_name(
                node.variable,
                self.parameter_location,
                self.ast,
                output
            )
            return reference_stack
        else:
            raise Exception("Unknown value")
