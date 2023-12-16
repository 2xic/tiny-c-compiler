"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal, WhileConditional, VariableAddressReference, VariableAddressDereference


class AsmOutputStream:
    def __init__(self, name) -> None:
        self.name = name
        self.debug = True
        self.is_main = name == "main"
        self.output_stream = [
            """
.text
    .global _start
_start:
            """            
        ] if self.name == "main" else [
f"""
{name}: 
    movl $0, %eax
"""]
        self.variables_stack_location = {}
        self.stack_location_offset = 0
        # We will never pop it off the stack, 
    
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
            "write":SyswriteMapping()
        }
        self.global_variables = {}
        self.message_counter = 2


    def get_asm(self):
        """
        Okay, currently we don't have any root_file which maybe is an issue ?
        """
        # we need to start from the main file ? 
        print(self.ast)
        assert isinstance(self.ast, File)
        assert "main" in self.ast.functions
        
        main_function_output = AsmOutputStream(
            name="main"
        )
        self.convert_nodes(self.ast.functions["main"], main_function_output)
        other_functions = []
        global_variables = []
        for i in self.ast.global_variables:
            function_code = AsmOutputStream(
                name=i
            )
            function_code.output_stream = []
            self.convert_nodes(self.ast.global_variables[i], function_code)
            # Insert after the init code
            main_function_output.output_stream = [main_function_output.output_stream[0], ] + function_code.output_stream + main_function_output.output_stream[1:]


        for i in self.ast.functions:
            if i != "main":
                function_code = AsmOutputStream(
                    name=i
                )
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
            if node.parent is None:
                self.data_sections.append(
                    f"\t{node.name}: .long 0"
                )
                print(node.value)
                if isinstance(node.value, NumericValue):
                    output.append(
                        f"\tmovl ${node.value.value}, {node.name}"
                    )
                else:
                    raise Exception("Unsupported global variable value")
            else:
                if not node.value is None:
                    # Else the node has to write the data to %eax at some point during the evaluation
                    if isinstance(node.value, NumericValue):
                        output.append(
                            "\t"+ output.get_or_set_stack_location(node.name, node.value.value),
                            comment=f"Referencing {node.name} assigned"
                        )
                    elif isinstance(node.value, VariableReference):
                        output.append(
                            "\t"+ output.get_or_set_stack_location(node.name, 0),
                            comment=f"Referencing {node.name} assigned"
                        )
                        stack = output.get_stack_value(node.value.variable) 
                        output.append(
                            f"\tmovl {stack}, %eax",
                            comment=f"Copying item from variable {node.value.variable}"
                        )
                        next_variable = output.get_or_set_stack_location(node.name, None)
                        output.append(
                            f"\tmovl %eax, {next_variable}",
                            comment=f"Referencing {node.name} assigned"
                        )
                    elif isinstance(node.value, VariableAddressReference):
                        location = output.get_memory_offset(node.value.variable.variable)
                        output.append(
                            "\t"+ output.get_or_set_stack_location(node.name, location),
                            comment=f"({node.name}) Storing variable reference for {node.value.variable.variable} "
                        )
                    else:
                        output.append(
                            "\t"+ output.get_or_set_stack_location(node.name, 0),
                            comment=f"Referencing {node.name} assigned"
                        )
                        stack = output.get_stack_value(node.name) 
                        self.convert_nodes(node.value, output)
                        output.append(
                            f"\tmovl %eax, {stack}",
                            comment=f"Referencing {node.name} assigned from a underlying node"
                        )
                else:
                    # still need to push a empty item to the stack to allocate it 
                    output.append(
                        "\t"+ output.get_or_set_stack_location(node.name, 0),
                        comment=f"{node.name} allocated"
                    )
            output.append(
                f"\tmovl $0, %eax",
                comment="I zero out after assignment"
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
                    output.append(self.create_sys_exit("%eax", output))
                else:
                    output.append(self.create_sys_exit(node.value, output))
            else:
                if isinstance(node.value, NumericValue):
                    # We return a static value ? 
                    # okay 
                    output.append(f"\tmovl    ${node.value.value}, %eax")
                elif isinstance(node.value, MathOp):
                    self.convert_nodes(node.value, output)
                elif isinstance(node.value, VariableReference):
                    stack = output.get_stack_value(node.value.variable)
                    output.append(
                        f"\tmov {stack}, %rax",
                        comment=f"Move stack value into rsp "
                    )
                else:
                    raise Exception("Unknown retunr op")
                # TODO: We need to clear the push pop ...

                if len(output.variables_stack_location):
                    #print(output.variables_stack_location)
                    # RESTORE THE RSP to before we got any function arguments
                    output.append(
                        f"\tmov %rsp, %rbx",
                        comment=f"Move the rsp on return"
                    )
                    stack = len(output.variables_stack_location) * 8
                    output.append(
                        f"\tadd ${stack}, %rbx",
                        comment=f"Reduce the rsp to correct offset on return"
                    )
                    # We now have the variable pointer in %rbx
                    output.append(
                        f"\tmov %rbx, %rsp",
                        comment=f"Move the pointer value into rbx on return"
                    )

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
            # This should also zero out eax ....
            # ^ technically I think we should zero eax at a different point, but okay
            output.append(
                f"\tmovl $0, %eax"
            )
            # do the math
            if isinstance(node.value, NumericValue):
                if isinstance(node.v_reference, VariableAddressDereference):
                    # TODO: CLean this up ...
                    parameter_index = self.is_variable_function_parameter(node.v_reference.value.variable)

                    stack = None
                    if parameter_index == -1:
                        stack = output.get_variable_offset(node.v_reference.value.variable)
                    else:
                        parameter_arguments = len(self.current_function.parameters.child_nodes) + len(output.variables_stack_location)
                        print((node.v_reference.value.variable, parameter_index))
                        stack = output.get_argument_stack_offset(
                            parameter_index,
                            parameter_arguments
                        ) 


                    # Dereference = You move memory into memory ...
                    # This is the location of the variable pointer
                    output.append(
                        f"\tmov %rsp, %rax",
                        comment=f"Move the rsp "
                    )
                    output.append(
                        f"\tadd ${stack}, %rax",
                        comment=f"Reduce the rsp to correct offset"
                    )
                    # We now have the variable pointer in %rax
                    output.append(
                        f"\tmov (%rax), %rax",
                        comment=f"Move the pointer value into rax "
                    )
                    output.append(
                        f"\tmovq ${node.value.value}, (%rax)",
                        comment=f"Assign to rsp offset"
                    )
                    pass
                else:
                    reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                    output.append(
                        f"\tmovl ${node.value.value}, {reference_stack}"
                    )
            else:
                self.convert_nodes(node.value, output)
                reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                output.append(
                    f"\tmovl %eax, {reference_stack}"
                )
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
                            output.append(f"\tpush ${i.value}", comment="call argument")
                        elif isinstance(i, StringValue):
                            print("WRITE STRINGS To RO SECTION!")
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
                        # RESTORE THE RSP to before we got any function arguments
                        # WE USE RBX HERE AS RAX IS USED FOR RETURN ARGUMENTS
                        output.append(
                            f"\tmov %rsp, %rbx",
                            comment=f"Move the rsp "
                        )
                        stack = len(node.parameters.child_nodes) * 8
                        output.append(
                            f"\tadd ${stack}, %rbx",
                            comment=f"Reduce the rsp to correct offset"
                        )
                        # We now have the variable pointer in %rbx
                        output.append(
                            f"\tmov %rbx, %rsp",
                            comment=f"Move the pointer value into rbx "
                        )
        elif isinstance(node, Conditionals):
            self.convert_nodes(node.if_condition, output)
            # Then we need to jump 
            # Then we can next condition, but not write to it yet.  
            if node.else_condition is not None:
                self.convert_nodes(node.else_condition, output)
        elif isinstance(node, IfCondition):
            self.convert_nodes(node.condition, output)
            assert isinstance(node.parent, Conditionals), node.parent
            #assert isinstance(node.parent.parent, Conditionals), node.parent.parent
            # todo: hardcoded ... fix
            # also this should not be applied here lol.
            end_of_id = node.parent.id
            if node.parent.else_condition is not None:
                output.append(
                    f"\tjne loc_{node.parent.else_condition.id}"
                )
            else:
                output.append(
                    f"\tjne end_of_if_{end_of_id}"
                )
            output.append(f"loc_{node.id}:")
            self.convert_nodes(node.body, output)
            output.append(f"\tjmp end_of_if_{end_of_id}")
        elif isinstance(node, ElseCondition):
            output.append(f"loc_{node.id}:")
            self.convert_nodes(node.body, output)
        elif isinstance(node, Equal):
            # I want to simple resolve here, variable reference are hard to think about ... 
            #a: VariableReference = node.a 
            parameter_index = self.is_variable_function_parameter(node.a.variable)
            reference_stack = None
            if parameter_index == -1:
                reference_stack = output.get_or_set_stack_location(node.a.variable, None)
            else:
                parameter_arguments = len(self.current_function.parameters.child_nodes) + len(output.variables_stack_location)
                reference_stack = output.get_argument_stack_offset(
                    parameter_index,
                    parameter_arguments
                ) + "(%rsp)"

            b: NumericValue = node.b
            output.append(
                f"\tcmpl ${b.value}, {reference_stack}",
                comment=f"Comparing against {node.a.variable}"
            )
        elif isinstance(node, WhileConditional):
            # Need to check this and then jump ...
            output.append("jmp loop1")
            # Jump to the conditional
            output.append("cloop1:")
#            print(node.body)
            self.convert_nodes(node.body, output)
            output.append("\tloop1:")
            self.convert_nodes(node.conditional, output)
            output.append("je cloop1")
        else:
            raise Exception("Unknown node " + str(node))    
    
    def handle_math_opcodes(self, node, output):
        if isinstance(node, NumericValue):
            output.append(f"\taddl ${node.value}, %eax")
        elif isinstance(node, MathOp):
            self.convert_nodes(node, output)                
        elif isinstance(node, FunctionCall):
            self.backup_eax_then_add_restore(node, output)
        elif node is None:
            pass
        elif isinstance(node, VariableReference):
            # This way of looking up the arguments should be made illegal, plz fix it.
            found_match = False
            for index, i in enumerate(self.current_function.parameters.child_nodes):
                if i.name == node.variable:
                    output.append(f"\taddl {8 * (index + 1)}(%rsp), %eax")
                    found_match = True
                    break
            if not found_match:
                reference_stack = output.get_or_set_stack_location(node.variable, None)
                output.append(f"\taddl {reference_stack}, %eax")

        else:
            raise Exception(f"Unknown math op node ({node})")
        
    def backup_eax_then_add_restore(self, node, output):
        output.append("\tmovl %eax, %ebx") # copy over the value
        self.convert_nodes(node, output)
        output.append(
            f"\taddl %ebx, %eax",
        )


    def create_sys_exit(self, exit_code, output: AsmOutputStream):
        if isinstance(exit_code, NumericValue):
            return f"""
        movl    ${exit_code.value}, %ebx
        movl    $1, %eax
        int     $0x80
            """
        elif isinstance(exit_code, VariableReference):
            if exit_code.variable in self.ast.global_variables:
                print(exit_code.variable)
                return f"""
                    movl    {exit_code.variable}, %ebx
                    movl    $1, %eax
                    int     $0x80
                """
            else:
                stack_location = output.get_or_set_stack_location(exit_code.variable, None)
                return f"""
            movl    {stack_location}, %ebx
            movl    $1, %eax
            int     $0x80
                """
        else:
            # Hm - not ideal way to implement this but works
            print(exit_code)
            return f"""
        movl    {exit_code}, %ebx
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

class SyswriteMapping:
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
#        output.append(
#            f"\tlea     {message_id}(%si), %rsi",
#        )
        output.append(
            f"\tlea     {message_id}(%rip), %rsi",
        )
        output.append(
            f"\tmov     ${len(string_value)}, %rdx"
        )
        output.append(
            "\tsyscall"
        )
