from ..ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal, WhileConditional, VariableAddressReference, VariableAddressDereference, StructMemberAccess, StructMemberDereferenceAccess, ExternalFunctionDefinition, NotEqual, ElseIfCondition, ForLoop, BinaryOperation
from .asm_output_stream import AsmOutputStream

"""
One of the most common operations is moving memory with the current assembly setup.
"""
class Register:
    def __init__(self, name) -> None:
        self.nme = name
    
    def __str__(self) -> str:
        return f"%{self.nme}"

    def __repr__(self) -> str:
        return self.__str__()

class MemoryLocation:
    def __init__(self, offset, register: Register) -> None:
        self.offset = offset
        self.register = register
    
    def __str__(self) -> str:
        if self.offset != 0:
            return f"{self.offset}({str(self.register)})"
        else:
            return f"({str(self.register)})"

    def __repr__(self) -> str:
        return self.__str__()


class StackLocation(MemoryLocation):
    def __init__(self, offset) -> None:
        super().__init__(offset, Register("rsp"))
        self.offset = offset


class ParameterLocation:
    def __init__(self, current_function) -> None:
        self.current_function = current_function
        self.parameters = self.current_function.parameters.child_nodes
        self.parameter_names = {
            entry.name: entry for entry in self.parameters
        }

    def get_variable(self, variable):
        location = self.get_variable_function_parameter_index(variable)
        if location == -1:
            return None
        else:
            return self.parameters[location]

    def get_variable_function_parameter_index(self, variable):
        parameter_index = -1 # 
        for index, i in enumerate(self.parameters):
            if i.name == variable:
                parameter_index = index
                break
        return parameter_index

    """
    Get stack variable dereferenced
    """
    def get_stack_variable_value(self, variable_name, output: AsmOutputStream):
        return str(self.get_stack_variable_offset(variable_name, output)) + "(%rsp)"

    """
    Find the variable location on the stack (both local + call arguments)
    """
    def get_stack_variable_offset(self, variable_name, output: AsmOutputStream):
        parameter_index = self.get_variable_function_parameter_index(variable_name)

        stack_offset = None
        if parameter_index == -1:
            stack_offset = output.get_variable_offset(variable_name)
        else:
            parameter_arguments = self.get_parameter_nodes(output)
            stack_offset = output.get_argument_stack_offset(
                parameter_index,
                parameter_arguments
            )
        return stack_offset
    
    def get_parameter_nodes(self, output: AsmOutputStream):
        return len(self.current_function.parameters.child_nodes) + len(output.variables_stack_location)

class VariableLocation:
    def __init__(self, value) -> None:
        self.value = value

    @staticmethod
    def from_global_variable(name):
        return VariableLocation(name)

    @staticmethod
    def from_variable_reference(variable: str, output: AsmOutputStream):
        # Find the place in memory that the variable is store so loading is simple
        return VariableLocation(output.get_or_set_stack_location(variable, None))

    @staticmethod
    def from_variable_address_reference(variable: str, parameter: ParameterLocation, ast: File, output: AsmOutputStream):
        # Find the memory address that the variable is store so loading is simple
        parameter_offset = parameter.get_variable_function_parameter_index(variable)
        # TODO: This should also be an universal api
        if parameter_offset != -1:
            offset = output.get_argument_stack_offset(
                parameter_offset,
                parameter.get_parameter_nodes(output)
            )
            #output.append(f"mov {value}, %rdx", comment=f"Load in the argument location")
            #return Register("rdx")
            # TODO: Move this into another section
            output.append("", comment=f"[Start adjust rsp to access function parameter {variable}]")
            output.append("mov %rsp, %rdx")
            output.append(f"add ${offset}, %rdx", comment=f"Adjusting the pointer access at location for variable")
            output.append("", comment="[end adjust rsp]")
            return Register("rdx")

        offset = output.get_memory_offset(variable)
        if offset == -1:
            return VariableLocation("%rsp")
        else:
            # TODO: Move this into another section
            output.append("", comment=f"[Start adjust rsp to access {variable}]")
            output.append("mov %rsp, %rdx")
            output.append(f"add ${offset}, %rdx", comment=f"Adjusting the pointer access at location for variable")
            output.append("", comment="[end adjust rsp]")
            return Register("rdx")

    
    @staticmethod
    def from_variable_name(variable: str, parameter: ParameterLocation, ast: File, output: AsmOutputStream):
        if variable in ast.global_variables:
            return VariableLocation.from_global_variable(variable)
        elif parameter.get_variable_function_parameter_index(variable) != -1:
            # TODO: Fix this, I don't want to pass reference here
            return VariableLocation(parameter.get_stack_variable_offset(variable, output) + "(%rsp)")            
        else:
            return VariableLocation.from_variable_reference(variable, output)

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class PushLocation:
    def __init__(self, name) -> None:
        self.name = name

    @staticmethod
    def variable(name):
        return PushLocation(name)
    
    @staticmethod
    def argument():
        return PushLocation(None)


def load_value(value, target, output: AsmOutputStream):
    assert isinstance(target, Register) or isinstance(target, MemoryLocation) or isinstance(target, StackLocation) or isinstance(target, VariableLocation) or isinstance(target, PushLocation) , "Bad load value"

    if isinstance(target, PushLocation):
        # None = not variable
        if target.name is not None:
            output.get_or_set_stack_location(target.name, None)
        if isinstance(value, NumericValue):
            return f"pushq ${value.value}"
        elif isinstance(value, Register):
            return f"pushq {str(value)}"
        elif isinstance(value, VariableLocation):
            return f"pushq {str(value)}"
        elif isinstance(value, MemoryLocation):
            return f"pushq {str(value)}"
        else:
            raise Exception(f"Unexpected push value {str(value)}")        
    else:
        if isinstance(value, NumericValue):
            if isinstance(target, Register):
                return f"mov ${value.value}, {str(target)}"
            else:
                return f"movl ${value.value}, {str(target)}"
        elif isinstance(value, VariableReference):
            if value.variable in output.global_variables:
                return f"mov {value.variable}, {str(target)}"
            else:
                stack = output.get_stack_value(value.variable)
                return f"mov {stack}, {str(target)}"
        elif isinstance(value, Register):
            return f"mov {str(value)}, {str(target)}"
        elif isinstance(value, VariableLocation):
            return f"mov {str(value)}, {str(target)}"
        elif isinstance(value, StackLocation):
            return f"mov {str(value)}, {str(target)}"
        elif isinstance(value, MemoryLocation):
            return f"mov {str(value)}, {str(target)}"
        else:
            raise Exception(f"Unexpected value {str(value)}")
        