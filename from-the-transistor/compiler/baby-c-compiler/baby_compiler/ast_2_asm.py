"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal, WhileConditional, VariableAddressReference, VariableAddressDereference
from .exceptions import InvalidSyntax

class AsmOutputStream:
    def __init__(self, name, global_variables, output_stream) -> None:
        self.name = name
        self.debug = True
        self.is_main = name == "main"
        self.output_stream = output_stream
        self.variables_stack_location = {}
        self.global_variables = global_variables
        self.stack_location_offset = 0
        # We will never pop it off the stack, 

    @staticmethod
    def main_function(global_variables):
        return AsmOutputStream("main", global_variables,  [
            """
            .text
                .global _start
            _start:
            """            
        ])
    
    @staticmethod
    def defined_function(name, global_variables):
        return AsmOutputStream(name, global_variables,  [
            f"""
                {name}: 
                    movl $0, %eax
            """            
        ])

    @staticmethod
    def create_global_variables():
        return AsmOutputStream("var", {},  [])
    
    def get_or_set_stack_location(self, name, value):
        assert len(name.split(" ")) == 1
        if not name in self.variables_stack_location:
            self.variables_stack_location[name] = (len(self.variables_stack_location) + 1)
            self.stack_location_offset += 1     
        # Size of the stack - location of the variable is where we should read :) 
        # Depending on the size of the stack is how far we need to look back!
        # Memory reference
        if value is None:
            return self.get_stack_value(name)
        elif type(value) == int or  value.isnumeric():
            return f"pushq ${value}"
        else:
            return f"pushq {value}"
        
    def get_stack_value(self, name):
        # Note: In this case we do dereference the value
        location = self.get_variable_offset(name)
        return f"{location}(%rsp)"
    
    def get_argument_stack_offset(self, index, size):
        # Argument would be at the location 1 + {size - index}
        location = ((size - index) ) * 8 # Always add one for the ret
        return f"{location}"

    def get_memory_offset(self, name):
        # This should reference the memory address
        # THIS SHOULD NOT DEREFERENCE
        location = self.get_variable_offset(name)
        assert location == 0
        return f"%rsp"
    

    def get_variable_offset(self, name):
        delta = (self.stack_location_offset - self.variables_stack_location[name])
        location = delta  * 8
        return location

    def append(self, text, comment=None):
        if self.debug:
            if comment is None:
                self.output_stream.append(text)
            else:
                self.output_stream.append(text + " # " + comment)
        else:
            self.output_stream.append(text)


class Ast2Asm:
    def __init__(self, ast: File) -> None:
        self.ast = ast
        """
        We could also do section .data
        """
        self.output_asm = [
        ]
        self.data_sections = [
"""
.data
"""
        ]

        # TODO: Make this part of the node instead
        self.current_function = None
        self.built_in_functions = {
            "write":SysWriteMapping(),
            "brk": Brk(),
        }
        self.message_counter = 2


    def get_asm(self):
        """
        Okay, currently we don't have any root_file which maybe is an issue ?
        """
        # we need to start from the main file ? 
        assert isinstance(self.ast, File)
        assert "main" in self.ast.functions
        # Load the main function
        main_function_output = AsmOutputStream.main_function(self.ast.global_variables)
        self.convert_nodes(self.ast.functions["main"], main_function_output)

        # Load global variables
        global_variables = []
        for i in self.ast.global_variables:
            function_code = AsmOutputStream.create_global_variables()
            self.convert_nodes(self.ast.global_variables[i], function_code)
            # Insert after the init code
            # TODO: Make the output stream handle the scoep better so you just insert after _start
            main_function_output.output_stream = [main_function_output.output_stream[0], ] + function_code.output_stream + main_function_output.output_stream[1:]

        # Load the 
        other_functions = []
        for i in self.ast.functions:
            if i != "main":
                function_code = AsmOutputStream.defined_function(i, self.ast.global_variables)
                self.convert_nodes(self.ast.functions[i], function_code)
                other_functions += function_code.output_stream

        # Need to insert one new lien at the end else the compiler is mad
        combined = global_variables + main_function_output.output_stream + other_functions + self.data_sections
        return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(combined).split("\n")))) + "\n"

    def convert_nodes(self, node, output: AsmOutputStream):
        if isinstance(node, File):
            return self.convert_nodes(node, output)
        elif isinstance(node, FunctionDefinition):
            """
            On a function call our stack looks like this
            [parent function arguments]
            [function call arguments]
            [return address]
            [function arguments]
            .... We need to adjust for that .... 
            """
            self.current_function = node
            self.convert_nodes(node.body, output)
        elif isinstance(node, VariableDeclaration):
            if node.name in output.variables_stack_location:
                raise InvalidSyntax(f"Invalid - re-declaration of variable of {node.name}")
            if node.parent is None:
                # This is global variable so we store it in the .data section
                self.data_sections.append(
                    f"\t{node.name}: .long 0"
                )
                if isinstance(node.value, NumericValue):
                    output.append(
                        load_value(node.value, VariableLocation(node.name), output)
                    )
                else:
                    raise Exception("Unsupported global variable value")
            else:
                if not node.value is None:
                    # Else the node has to write the data to %eax at some point during the evaluation
                    if isinstance(node.value, NumericValue):
                        output.append(
                            load_value(
                                node.value,
                                PushLocation(node.name),
                                output,
                            )
                        )
                    elif isinstance(node.value, VariableReference):
                        # Load the old value into eax
                        output.append(
                            load_value(
                                VariableLocation.from_variable_reference(node.value.variable, output),
                                Register("eax"),
                                output,
                            )
                        )
                        # Store the new value from the old value 
                        output.append(
                            load_value(
                                Register("rax"),
                                PushLocation(node.name),
                                output,
                            )
                        )
                    elif isinstance(node.value, VariableAddressReference):
                        output.append(
                            load_value(
                                VariableLocation.from_variable_address_reference(node.value.variable.variable, output),
                                PushLocation(node.name),
                                output,
                            )
                        )
                    else:
                        # Store 0 to allocate
                        output.append(
                            load_value(
                                NumericValue(0),
                                PushLocation(node.name),
                                output,
                            )
                        )
                        # Execute the node restore the value
                        self.convert_nodes(node.value, output)
                        output.append(
                            load_value(
                                Register("eax"),
                                VariableLocation.from_variable_reference(node.name, output),
                                output,
                            )
                        )
                        output.append(
                            f"\tmovl $0, %eax",
                            comment="I zero out after assignment"
                        )
                else:
                    # still need to push a empty item to the stack to allocate it 
                    output.append(
                        load_value(
                            NumericValue(0),
                            PushLocation(node.name),
                            output,
                        )
                    )
        elif isinstance(node, FunctionBody):
            for i in node.child_nodes:
                self.convert_nodes(i, output)
                if isinstance(i, Conditionals):
                    output.append(f"end_of_if_{i.id}:")
        elif isinstance(node, ReturnDefinition):
            if output.is_main:
                # technically it should only be a exit if this is the main opcode ...
                if isinstance(node.value, MathOp):
                    # Unwrap it ... push add push add ..
                    # We will store the results into memory ...
                    self.convert_nodes(node.value, output)
                    output.append(self.create_sys_exit(Register("eax"), output))
                else:
                    output.append(self.create_sys_exit(node.value, output))
            else:
                if isinstance(node.value, NumericValue):
                    output.append(load_value(node.value, Register("eax"), output))
                elif isinstance(node.value, MathOp):
                    self.convert_nodes(node.value, output)
                elif isinstance(node.value, VariableReference):
                    output.append(load_value(node.value, Register("rax"), output))
                else:
                    raise Exception("Unknown return opcode value")
                # Reset the local values            
                if len(output.variables_stack_location):
                    stack = len(output.variables_stack_location) * 8
                    self.reset_stack_pointer(stack, output, reason="return statement")
                output.append("\tret")

        elif isinstance(node, MathOp):
            """
            The add opcode from assembly is like this
            ADD immediate value to a register
            """
            # We write to EAX, but should be able to do more dynamic allocations soon
            self.handle_math_opcodes(node.expr_1, output)
            self.handle_math_opcodes(node.expr_2, output)
        elif isinstance(node, VariableAssignment):
            if isinstance(node.value, NumericValue):
                if isinstance(node.v_reference, VariableAddressDereference):
                    stack_offset = self.get_stack_variable_offset(node.v_reference.value.variable, output)
                    # Dereference = You move memory into memory ...
                    # This is the location of the variable pointer
                    self.load_stack_value_to_rax(stack_offset, output)
                    # Then we load the value
                    output.append(
                        f"\tmovl ${node.value.value}, (%rax)",
                        comment=f"Assign to rsp offset"
                    )
                else:
                    reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                    output.append(
                        f"\tmovl ${node.value.value}, {reference_stack}"
                    )
            else:
                output.append(
                    f"\tmovl $0, %eax",
                    comment="I zero out after assignment"
                )
                # In the case of function calls etc
                self.convert_nodes(node.value, output)
                reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                output.append(
                    f"\tmovl %eax, {reference_stack}"
                )
                # We need to zero out eax after a function call
                output.append(
                    f"\tmovl $0, %eax",
                    comment="I zero out after assignment"
                )
        elif isinstance(node, FunctionCall):
               if node.function_name in self.built_in_functions:
                    self.built_in_functions[node.function_name].convert(
                        node.parameters.child_nodes,
                        self,
                        output
                    )
               else:
                    for i in node.parameters.child_nodes:
                        if isinstance(i, NumericValue):
                            output.append(
                                load_value(
                                    i,
                                    PushLocation.argument(),
                                    output,
                                )
                            )
                        elif isinstance(i, StringValue):
                            print("Write strings to the RO section")
                        elif isinstance(i, VariableReference):
                            # You just push the variable location bro
                            location = output.get_stack_value(i.variable)
                            output.append(
                                "\t"+ "pushq " + location,
                                comment=f"Pushing pointer argument of {i.variable}"
                            )
                        else:
                            raise Exception("Unknown parameter")
                    output.append(
                        f"\tcall {node.function_name}"
                    )
                    # Now we need to clear the fields ... 
                    if len(node.parameters.child_nodes):
                        stack = len(node.parameters.child_nodes) * 8
                        self.reset_stack_pointer(stack, output, "Input arguments to function")

        elif isinstance(node, Conditionals):
            self.convert_nodes(node.if_condition, output)
            # Then we need to jump 
            # Then we can next condition, but not write to it yet.  
            if node.else_condition is not None:
                self.convert_nodes(node.else_condition, output)
        elif isinstance(node, IfCondition):
            self.convert_nodes(node.condition, output)
            assert isinstance(node.parent, Conditionals), node.parent
            # Use the id for the condition
            end_of_id = node.parent.id
            # If we have a if and else then we check for the else condition 
            if node.parent.else_condition is not None:
                output.append(
                    f"\tjne loc_{node.parent.else_condition.id}"
                )
            else:
                # We just check for the if conditional
                output.append(
                    f"\tjne end_of_if_{end_of_id}"
                )
            output.append(f"loc_{node.id}:")
            # Load in the main body
            self.convert_nodes(node.body, output)
            output.append(f"\tjmp end_of_if_{end_of_id}")
        elif isinstance(node, ElseCondition):
            output.append(f"loc_{node.id}:")
            self.convert_nodes(node.body, output)
        elif isinstance(node, Equal):
            reference_stack = self.get_stack_variable_value(node.a.variable, output)
            b: NumericValue = node.b
            output.append(
                f"\tcmpl ${b.value}, {reference_stack}",
                comment=f"Comparing against {node.a.variable}"
            )
        elif isinstance(node, WhileConditional):
            # Need to check this and then jump ...
            output.append(f"jmp loop{node.id}")
            # Jump to the conditional
            output.append(f"cloop{node.id}:")
            # Parse the body data
            self.convert_nodes(node.body, output)
            # define the loop start + conditional
            output.append(f"\tloop{node.id}:")
            self.convert_nodes(node.conditional, output)
            # Jump to while loop if true
            output.append(f"je cloop{node.id}")
        else:
            raise Exception("Unknown node " + str(node))    
    
    def handle_math_opcodes(self, node, output):
        if isinstance(node, NumericValue):
            output.append(f"\taddl ${node.value}, %eax")
        elif isinstance(node, MathOp):
            self.convert_nodes(node, output)                
        elif isinstance(node, FunctionCall):
            # Do a backup and then restore 
            output.append("\tmovl %eax, %ebx", comment="Backup current value")
            self.convert_nodes(node, output)
            output.append(
                f"\taddl %ebx, %eax",
                comment="Restore the current value",
            )
        elif isinstance(node, VariableReference):
            reference_stack = self.get_stack_variable_value(node.variable, output)
            output.append(f"\taddl {reference_stack}, %eax")
        else:
            raise Exception(f"Unknown math op node ({node})")

    """
    Get stack variable dereferenced
    """
    def get_stack_variable_value(self, variable_name, output: AsmOutputStream):
        return str(self.get_stack_variable_offset(variable_name, output)) + "(%rsp)"

    """
    Find the variable location on the stack (both local + call arguments)
    """
    def get_stack_variable_offset(self, variable_name, output: AsmOutputStream):
        parameter_index = self.is_variable_function_parameter(variable_name)

        stack_offset = None
        if parameter_index == -1:
            stack_offset = output.get_variable_offset(variable_name)
        else:
            parameter_arguments = len(self.current_function.parameters.child_nodes) + len(output.variables_stack_location)
            stack_offset = output.get_argument_stack_offset(
                parameter_index,
                parameter_arguments
            )
        return stack_offset

    """
    This is used to for instance to reset after a function call

    Input should be the calculated offset to change
    """
    def reset_stack_pointer(self, stack_offset, output: AsmOutputStream, reason: str):
        output.append(
            f"\tmov %rsp, %rbx",
            comment=f"Move the rsp because of {reason}"
        )
        output.append(
            f"\tadd ${stack_offset}, %rbx",
            comment=f"Reduce the rsp to correct offset because of {reason}"
        )
        output.append(
            f"\tmov %rbx, %rsp",
            comment=f"Move the pointer value into rbx because of {reason}"
        )
    
    """
    Dereference the value at the given stack offset into rax
    """
    def load_stack_value_to_rax(self, stack_offset, output: AsmOutputStream):
        output.append(
            f"\tmov %rsp, %rax",
            comment=f"Move the rsp "
        )
        output.append(
            f"\tadd ${stack_offset}, %rax",
            comment=f"Reduce the rsp to correct offset"
        )
        # We now have the variable pointer in %rax
        output.append(
            f"\tmov (%rax), %rax",
            comment=f"Move the pointer value into rax "
        )

    def create_sys_exit(self, exit_code, output: AsmOutputStream):
        move_value = load_value(exit_code, Register("ebx"), output)
        return f"""
            {move_value}
            movl    $1, %eax
            int     $0x80
        """

    def is_variable_function_parameter(self, variable):
        parameter_index = -1 # 
        for index, i in enumerate(self.current_function.parameters.child_nodes):
            if i.name == variable:
                parameter_index = index
                break
        return parameter_index

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

class StackLocation:
    def __init__(self, offset) -> None:
        self.offset = offset
    
    def __str__(self) -> str:
        return f"{self.offset}(%rsp)"

    def __repr__(self) -> str:
        return self.__str__()

class VariableLocation:
    def __init__(self, value) -> None:
        self.value = value

    @staticmethod
    def from_global_variable(name):
        return VariableLocation(name)

    @staticmethod
    def from_variable_reference(variable: str, output: AsmOutputStream):
        # Find the place in memory that the variable is store so loading is simple
        #raise Exception("Not implemented")
        return VariableLocation(output.get_or_set_stack_location(variable, None))

    @staticmethod
    def from_variable_address_reference(variable: str, output: AsmOutputStream):
        # Find the place in memory that the variable is store so loading is simple
        return VariableLocation(output.get_memory_offset(variable))

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
    assert isinstance(target, Register) or isinstance(target, StackLocation) or isinstance(target, VariableLocation) or isinstance(target, PushLocation) 

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
        else:
            raise Exception(f"Unexpected push value {str(value)}")
    else:
        if isinstance(value, NumericValue):
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
        else:
            raise Exception(f"Unexpected value {str(value)}")


class SysWriteMapping:
    def __init__(self) -> None:
        pass

    def convert(self, parameters, asm_root: Ast2Asm, output: AsmOutputStream):
        assert isinstance(parameters[0], NumericValue)
        assert isinstance(parameters[1], NumericValue)
        assert isinstance(parameters[2], StringValue)
        string_value = parameters[2].value
        message_id = f"message{asm_root.message_counter}"
        output.append(
            "\txor     %eax, %eax",
        )
        output.append(
            "\txor     %ebx, %ebx",
        )
        asm_root.message_counter += 1
        asm_root.data_sections.append(
            f"\t{message_id}:  .ascii  \"{string_value}\""
        )
        output.append(
            "\tmov     $1, %eax",
        )
        output.append(
            "\tmov     $1, %rdi",
        )
        output.append(
            f"\tlea     {message_id}(%rip), %rsi",
        )
        output.append(
            f"\tmov     ${len(string_value)}, %rdx"
        )
        output.append(
            "\tsyscall"
        )


class Brk:
    def __init__(self) -> None:
        pass

    def convert(self, parameters, asm_root: Ast2Asm, output: AsmOutputStream):
        """
        sbrk syscall 2 get program segment
            mov   $12, %rax         
            mov   $0, %rdi          
            syscall               
            """
        assert len(parameters) == 1
        value = None
        if isinstance(parameters[0], NumericValue):
            value = parameters[0].value
            value = f"${value}"
        elif isinstance(parameters[0], VariableReference):
            offset = output.get_stack_value(parameters[0].variable)
            value = offset
        else:
            raise Exception("Unknown parameter")
        output.append(
            "\tmov     $12, %rax",
        )
        output.append(
            f"\tmov     {value}, %rdi",
        )
        output.append(
            "\tsyscall"
        )
