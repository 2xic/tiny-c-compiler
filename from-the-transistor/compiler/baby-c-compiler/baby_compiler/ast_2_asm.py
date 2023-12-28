"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal, WhileConditional, VariableAddressReference, VariableAddressDereference, StructMemberAccess, StructMemberDereferenceAccess, ExternalFunctionDefinition, NotEqual, ElseIfCondition, ForLoop, BinaryOperation
from .exceptions import InvalidSyntax
from .utils import format_asm_output
from .code_generation.asm_output_stream import AsmOutputStream
from .code_generation.memory_operations import load_value, PushLocation, MemoryLocation, StackLocation, VariableLocation, Register, ParameterLocation


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
        self.parameter_location = None
        self.built_in_functions = {
            "write":SysWriteMapping(),
            "brk": Brk(),
        }
        self.message_counter = 2

    def get_asm(self):
        """
        Okay, currently we don't have any root_file which maybe is an issue ?
        """
        #print(self.ast)
        # we need to start from the main file ? 
        assert isinstance(self.ast, File), "Bad file"
        # Load the main function
        main_function_output = None
        if  "main" in self.ast.functions:
            main_function_output = AsmOutputStream.main_function(self.ast.global_variables)
            self.convert_nodes(self.ast.functions["main"], main_function_output)
        else:
            main_function_output = AsmOutputStream.text_section(self.ast.global_variables)

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
            if i in self.ast.external_functions:
                continue
            if i != "main":
                function_code = AsmOutputStream.defined_function(i, self.ast.global_variables)
                self.convert_nodes(self.ast.functions[i], function_code)
                other_functions += function_code.output_stream

        # Need to insert one new lien at the end else the compiler is mad
        combined = global_variables + main_function_output.output_stream + other_functions + self.data_sections
        return format_asm_output(combined)

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
            self.parameter_location = ParameterLocation(node)
            self.convert_nodes(node.body, output)
        elif isinstance(node, VariableDeclaration):
            output.variable_2_type[node.name] = node.type
            # TODO: Or in the function parameters
            if node.name in output.variables_stack_location:
                raise InvalidSyntax(f"Invalid - re-declaration of variable of {node.name}")
            if node.parent is None:
                # This is global variable so we store it in the .data section
                self.data_sections.append(
                    f"\t{node.name}: .long 0"
                )
                if isinstance(node.value, NumericValue):
                    output.append(
                        load_value(node.value, VariableLocation(node.name), output),
                        comment=f"{node.name} allocation"
                    )
                elif node.value is not None:
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
                            ),
                            comment=f"{node.name} allocation"
                        )
                    elif isinstance(node.value, VariableReference):
                        if isinstance(node.value.variable, StructMemberDereferenceAccess):
                            # Allocate the variable
                            output.append(
                                load_value(
                                    NumericValue(0),
                                    PushLocation(node.name),
                                    output,
                                ),
                                comment=f"Allocate the struct variable ({node.name})"
                            )

                            _ = self.get_struct_member_load(
                                node.value.variable,
                                "???",
                                output
                            )

                            # %rbx should now contain the value ... let's reassign it 
                            output.append(
                                load_value(
                                    MemoryLocation(0, Register("rbx")),
                                    Register("rax"),
                                    output,
                                ),
                                comment="Temp storage to speed it all up (reference)"
                            )
                            output.append(
                                load_value(
                                    Register("rax"),
                                    VariableLocation.from_variable_reference(node.name, output),
                                    output,
                                ),
                                comment="Load in the value of the rbx"
                            )                           
                            # Rbx now needs to be loaded somewhere ?
                        else:
                            # Load the old value into eax
                            output.append(
                                load_value(
                                    VariableLocation.from_variable_reference(node.value.variable, output),
                                    Register("rax"),
                                    output,
                                ),
                                comment=f"Load value ({node.value.variable}) into rax"
                            )
                            # Store the new value from the old value 
                            output.append(
                                load_value(
                                    Register("rax"),
                                    PushLocation(node.name),
                                    output,
                                ),
                                comment=f"what what ({str(node.value)})"
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
                            ),
                            comment=f"{node.name} allocation calls"
                        )
                        output.append("xor %rax, %rax")
                        # Execute the node restore the value
                        self.convert_nodes(node.value, output)
                        output.append(
                            load_value(
                                Register("eax"),
                                VariableLocation.from_variable_reference(node.name, output),
                                output,
                            ),
                            comment="Restore the value from the converted node"
                        )
                        # Reset the value 
                        output.append("xor %rax, %rax")
                elif "struct" in node.type.name:
                    self.put_struct_members_on_stack(
                        node.type.name,
                        node,
                        output          
                    )
                else:                
                    # still need to push a empty item to the stack to allocate it 
                    output.append(
                        load_value(
                            NumericValue(0),
                            PushLocation(node.name),
                            output,
                        ),
                        comment=f"{node.name} allocation"
                    )
        elif isinstance(node, FunctionBody):
            for i in node.child_nodes:
                self.convert_nodes(i, output)
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
                # Need to load the value for the return statement
                if isinstance(node.value, NumericValue):
                    output.append(load_value(node.value, Register("rax"), output))
                elif isinstance(node.value, MathOp):
                    self.convert_nodes(node.value, output)
                elif isinstance(node.value, VariableReference):
                    output.append(load_value(node.value, Register("rax"), output), comment=f"Loaded {node.value.variable} into rax")
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
        elif isinstance(node, BinaryOperation):
            if node.op =="++":
                reference_stack = self.parameter_location.get_stack_variable_value(node.expr_1.variable, output)
                output.append(f"\taddl $1, {reference_stack}", comment="Add the ++ to the reference stack")
            else:
                raise Exception("what is this? I don't know this op in binary op")
        elif isinstance(node, VariableAssignment):
            if isinstance(node.right_side, NumericValue):
                if isinstance(node.left_side, VariableAddressDereference):
                    # ASsign to the location of the variable
                    stack_offset = self.parameter_location.get_stack_variable_offset(node.left_side.value.variable, output)
                    # Dereference = You move memory into memory ...
                    # This is the location of the variable pointer
                    self.load_stack_value_to_rax(stack_offset, output)
                    # Then we load the value
                    output.append(
                        f"\tmovl ${node.right_side.value}, (%rax)",
                        comment=f"Assign to rsp offset"
                    )
                elif isinstance(node.left_side, StructMemberDereferenceAccess):
                    _ = self.get_struct_member_load(node.left_side, node.right_side, output)
                    output.append(
                        load_value(
                            node.right_side,
                            MemoryLocation(0, Register("rbx")),
                            output,
                        ),
                        comment=f"Load variable ({node.right_side}) into memory location"
                    )
                else:
                    # TODO: We allow strs in the left side, but should only use variable references.
                    reference_stack = None
                    if isinstance(node.left_side, StructMemberAccess):
                        variable_name = node.left_side.variable_reference + "_" + node.left_side.value
                        if variable_name in self.ast.global_variables:
                            reference_stack = VariableLocation.from_variable_name(
                                variable_name,
                                self.parameter_location,
                                self.ast,
                                output,
                            )
                    if reference_stack is None:
                        reference_stack = output.get_or_set_stack_location(node.left_side, None)
                    output.append(
                        f"\tmovl ${node.right_side.value}, {reference_stack}"
                    )
            elif isinstance(node.right_side, VariableReference):
                """
                TODO: Refactor all of this code section
                """
                if isinstance(node.left_side, StructMemberDereferenceAccess):
                    _ = self.get_struct_member_load(node.left_side, node.right_side.variable, output)
                    # load the variable value
                    output.append(
                        load_value(
                            StackLocation(self.parameter_location.get_stack_variable_offset(node.right_side.variable, output)),
                            Register("rdx"),
                            output,
                        ),
                        comment=f"Load variable ({node.right_side.variable}) into memory location of reference"
                    )
                    output.append(
                        load_value(
                            Register("rdx"),
                            MemoryLocation(0, Register("rbx")),
                            output,
                        ),
                        comment=f"Load value into rbx offset"
                    )
                elif isinstance(node.right_side, VariableReference) and isinstance(node.right_side.variable, StructMemberDereferenceAccess):
                    member_access = self.get_struct_member_load(node.right_side.variable, output)
                    output.append(
                        f"mov %rbx, {member_access}",
                        comment=f"Load variable ({node.right_side.variable}) into memory location"
                    )
                else:
                    output.append(
                        load_value(
                            StackLocation(self.parameter_location.get_stack_variable_offset(node.right_side.variable, output)),
                            Register("rbx"),
                            output,
                        ),
                        comment=f"Load value({node.right_side.variable}) before assignment"
                    )
                    output.append(
                        load_value(
                            Register("rbx"),
                            VariableLocation.from_variable_name(node.left_side, self.parameter_location, self.ast, output),
                            output,
                        ),
                        comment=f"Use loaded value for assignment ({node.left_side})"
                    )
            else:
                output.append(
                    f"\txor %rax, %rax",
                    comment="I zero out after assignment"
                )
                # In the case of function calls etc
                self.convert_nodes(node.right_side, output)
                reference_stack = output.get_or_set_stack_location(node.left_side, None)
                output.append(
                    f"\tmov %rax, {reference_stack}",
                    comment=f"Set the node result into variable {node.left_side}"
                )
                # We need to zero out rax after a function call
                output.append(
                    f"\txor %rax, %rax",
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
                len_calls_arguments = len(node.parameters.child_nodes)
                len_function_definition_arguments = len(self.ast.functions[node.function_name].parameters.child_nodes)
                if len_calls_arguments != len_function_definition_arguments:
                    raise InvalidSyntax()

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
                        raise Exception("Todo handle the string calls")
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
                    f"\tcall {node.function_name}@PLT"
                )
                # Now we need to clear the fields ... 
                if len_calls_arguments:
                    stack = len_calls_arguments * 8
                    self.reset_stack_pointer(stack, output, "Input arguments to function")
        elif isinstance(node, Conditionals):
            # We need to save this to restore it
            copy_of_variables = dict(output.variables_stack_location)
            copy_offset = int(output.stack_location_offset)
            # setup the conditional logic
            self.convert_nodes(node.if_condition.condition, output)
            # Use the id for the condition
            end_of_id = node.id
            # What we do in this case is to skip the region if not equal.
            jne_id = "jne" if isinstance(node.if_condition.condition, Equal) else "je"
            # If we have a if and else then we check for the else condition 
            else_condition = node.else_condition
            # Else if conditionals is good
            if len(node.else_if_conditions):
                # We construct a jump condition loop
                current_id_else = node.if_condition.id
                for i in node.else_if_conditions:
                    jne_id = "je" if isinstance(i.condition, Equal) else "jne"
                    output.append(
                        f"\t{jne_id} loc_{current_id_else}",
                        comment="Jump location"
                    )
                    current_id_else = i.id
                    self.convert_nodes(i.condition, output)
                output.append(
                    f"\t{jne_id} loc_{current_id_else}",
                    comment="Else if condition jump"
                )

                if else_condition is not None:
                    output.append(
                        f"\tjmp loc_{else_condition.id}",
                        comment="Else condition jump"
                    )
            else:
                if else_condition is not None:
                    # ... here we could have have a else if 
                    output.append(
                        f"\t{jne_id} loc_{else_condition.id}",
                        comment="Else condition jump"
                    )
                else:
                    # We just check for the if conditional
                    output.append(
                        f"\t{jne_id} end_of_if_{end_of_id}"
                    )
                    
            for i in node.child_nodes:
                if i is not None:
                    self.convert_nodes(i, output)
                    # TODO: Fix this hack
                    add_jump = not "ret" in output.output_stream[-1]

                    # TODO: Here we also need to reset the stack pointer ...
                    delta = output.stack_location_offset - copy_offset
                    self.reset_stack_pointer(delta * 8, output, "Reset after branch switch")
                    if add_jump:
                        # we create this after the conditional node
                        output.append(f"\tjmp end_of_if_{end_of_id}")

                    # Then we need to jump 
                    # Then we can next condition, but not write to it yet.  
                    output.variables_stack_location = copy_of_variables
                    output.stack_location_offset = copy_offset        
            # We always need to add this at the end
            output.append(f"end_of_if_{node.id}:")
        elif isinstance(node, IfCondition):
            output.append(f"loc_{node.id}:")
            # Load in the main body
            self.convert_nodes(node.body, output)
        elif isinstance(node, ElseIfCondition):
            output.append(f"loc_{node.id}:")
            # Load in the main body
            self.convert_nodes(node.body, output)
        elif isinstance(node, ElseCondition):
            output.append(f"loc_{node.id}:")
            self.convert_nodes(node.body, output)
        elif isinstance(node, Equal) or isinstance(node, NotEqual):
            # TODO: This should be a nicer abstraction
            reference_stack = None
            if node.a.variable in output.global_variables:
                reference_stack = f"{node.a.variable}"
            else:
                reference_stack = self.parameter_location.get_stack_variable_value(node.a.variable, output)
            b: NumericValue = node.b
            output.append(
                f"\tcmpl ${b.value}, {reference_stack}",
                comment=f"Comparing against {node.a.variable}"
            )
        elif isinstance(node, WhileConditional):
            copy_of_variables = dict(output.variables_stack_location)
            copy_offset = int(output.stack_location_offset)

            # Need to check this and then jump ...
            output.append(f"jmp loop{node.id}")
            # Jump to the conditional
            output.append(f"cloop{node.id}:")
            # Parse the body data
            self.convert_nodes(node.body, output)
            # Reset the stack pointer in case of local variables
            delta = output.stack_location_offset - copy_offset
            self.reset_stack_pointer(delta * 8, output, "Reset after branch switch")
            # We reset it back
            output.variables_stack_location = copy_of_variables
            output.stack_location_offset = copy_offset        
            # define the loop start + conditional
            output.append(f"\tloop{node.id}:")
            self.convert_nodes(node.conditional, output)
            # Jump to while loop if true
            jne_id = "je" if isinstance(node.conditional, Equal) else "jne"
            output.append(f"{jne_id} cloop{node.id}")
        elif isinstance(node, ForLoop):
            copy_of_variables = dict(output.variables_stack_location)
            copy_offset = int(output.stack_location_offset)

            # Need to check this and then jump ...
            self.convert_nodes(node.initialization_statement, output)
            output.append(f"jmp loop{node.id}")
            # Jump to the conditional
            output.append(f"cloop{node.id}:")
            # Parse the body data
            self.convert_nodes(node.body, output)
            self.convert_nodes(node.update_statement, output)

            # Reset the stack pointer in case of local variables
            delta = output.stack_location_offset - copy_offset
            self.reset_stack_pointer(delta * 8, output, "Reset after branch switch")
            # We reset it back
            output.variables_stack_location = copy_of_variables
            output.stack_location_offset = copy_offset        

            # define the loop start + conditional
            output.append(f"\tloop{node.id}:")
            self.convert_nodes(node.test_expression_statement, output)
            # Jump to while loop if true
            jne_id = "je" if isinstance(node.test_expression_statement, Equal) else "jne"
            output.append(f"{jne_id} cloop{node.id}")
        elif isinstance(node, ExternalFunctionDefinition):
            pass
        else:
            raise Exception("Unknown node " + str(node))    
    
    def handle_math_opcodes(self, node, output: AsmOutputStream):
        if isinstance(node, NumericValue):
            output.append(f"\taddl ${node.value}, %eax")
        elif isinstance(node, MathOp):
            self.convert_nodes(node, output)                
        elif isinstance(node, FunctionCall):
            # Do a backup and then restore 
            output.append("\tmovl %eax, %edx", comment="Backup current value")
            self.convert_nodes(node, output)
            output.append(
                f"\taddl %edx, %eax",
                comment="Restore the current value",
            )
        elif isinstance(node, VariableReference):
            # TODO: Fix the struct member access
            variable = node.variable
            if isinstance(variable, StructMemberAccess):
                new_variable = variable.variable_reference + "_" + variable.value
                if new_variable in self.ast.global_variables:
                    variable = new_variable
                    
            reference_stack = VariableLocation.from_variable_name(
                variable,
                self.parameter_location,
                self.ast,
                output
            )
            output.append(f"\taddl {reference_stack}, %eax", comment="Add the reference stack")
        else:
            raise Exception(f"Unknown math op node ({node})")

    """
    This is used to for instance to reset after a function call

    Input should be the calculated offset to change
    """
    def reset_stack_pointer(self, stack_offset, output: AsmOutputStream, reason: str):
        output.append("# [start] Restore the stack pointer")
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
        output.append("# [end] Restore the stack pointer")    

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
    
    def get_struct_member_index(self, node: StructMemberDereferenceAccess, output: AsmOutputStream):
        index = -1
        # TODO: This could also contain a function parameter.
        variable = None

        if node.variable_reference in output.variable_2_type:
            variable = output.variable_2_type[node.variable_reference]
        elif node.variable_reference + "_" + node.value in self.ast.global_variables:
            variable = self.ast.global_variables[node.variable_reference + "_" + node.value]
        else:
            # TODO: REmove this hardcoding
            if "a" in str(node.variable_reference):
                return 0
            raise Exception("Variable not found " + str(node.variable_reference))

        if isinstance(variable, VariableDeclaration):
            variable = variable.type
        name = variable.name.replace("*","").split(" ")[-1]
        for member_i, i in enumerate(self.ast.global_types[name].members):
            if i.name == node.value:
                index = member_i
                break
        return index
    """
    Struct member accesses
    """
    def get_struct_member_load(self, node: StructMemberDereferenceAccess, field_name, output: AsmOutputStream):
        """
        RBX 
        """
        print("Before")
        print(output.variables_stack_location)
        variable = VariableLocation.from_variable_name(node.variable_reference, self.parameter_location, self.ast, output)
        print("After form")
        print(output.variables_stack_location)
        member_access = StackLocation(
            VariableLocation.from_variable_name(
                node.variable_reference, self.parameter_location, self.ast, output
            )
            # self.parameter_location.get_stack_variable_offset(node.variable_reference, output)
        )
        print(output.variables_stack_location)
        index = self.get_struct_member_index(
            node,
            output
        )
        output.append(
            load_value(
                variable,
                Register("rbx"),
                output,
            ),
            comment=f"Load variable ({field_name}) reference into rbx from {member_access}"
        )
        if index != -1:
            if index != 0:
                #raise Exception("Need to adjust the pointer location for the size")                           
                output.append(f"add ${index * 8}, %rbx")
            return member_access
        else:
            raise Ellipsis("Did not find the struct variable location")

    def put_struct_members_on_stack(self, type_name, node: VariableDeclaration, output: AsmOutputStream):
        # For each member we allocate a variable ... bit hacky, but works for now
        if "*" in type_name:
            # We just load the pointer
            raise Exception("huh")
        else:
            # TODO: clean this up
            members = self.ast.global_types[type_name.split("struct ")[-1]]
            for i in members.members:
                name = type_name.split("struct ")[-1] + "_" + i.name
                if name in self.ast.global_variables:
                    print(i.name, name)
                else:
                    output.append(
                        load_value(
                            NumericValue(0),
                            PushLocation(node.name + "." + i.name),
                            output,
                        ),
                        comment="Load struct member " + str(i)
                    )

"""
TODO: Move this into a more logical place
"""

class SysWriteMapping:
    def __init__(self) -> None:
        pass

    def convert(self, parameters, asm_root: Ast2Asm, output: AsmOutputStream):
        assert isinstance(parameters[0], NumericValue), "Bad sys write"
        assert isinstance(parameters[1], NumericValue), "Bad sys write"
        assert isinstance(parameters[2], StringValue), "Bad sys write"
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
        assert len(parameters) == 1, "Bad parameter"
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
