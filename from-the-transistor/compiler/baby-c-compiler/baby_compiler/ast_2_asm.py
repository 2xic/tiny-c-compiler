"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal, WhileConditional, VariableAddressReference, VariableAddressDereference, StructMemberAccess, StructMemberDereferenceAccess, ExternalFunctionDefinition, NotEqual, ElseIfCondition, ForLoop, BinaryOperation
from .exceptions import InvalidSyntax
import re

class AsmOutputStream:
    def __init__(self, name, global_variables, output_stream) -> None:
        self.name = name
        self.debug = True
        self.is_main = name == "main"
        self.output_stream = output_stream
        self.variables_stack_location = {}
        # TODO: I don't want this to be retracked here
        self.variable_2_type = {}
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
    def text_section(global_variables):
        return AsmOutputStream("text", global_variables,  [
            """
            .text
            """            
        ])
    
    @staticmethod
    def defined_function(name, global_variables):
        return AsmOutputStream(name, global_variables,  [
            f"""
                .globl	{name}
                .type	{name}, @function
                {name}: 
                    movl $0, %eax
            """            
        ])

    @staticmethod
    def create_global_variables():
        return AsmOutputStream("var", {},  [])
    
    def get_or_set_stack_location(self, name, value):
        if isinstance(name, StructMemberAccess):
            name = name.get_path()
        elif isinstance(name, StructMemberDereferenceAccess):
            """
            The struct variable would be a segment reference.
            
            We need to know our pointer size position for the alignment
            """
            print(name, value)
            return "TODO"
        assert len(name.split(" ")) == 1, "Bad name"

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
        if isinstance(name, StructMemberAccess):
            name = name.get_path()
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
        assert location == 0, "Bad location"
        return f"%rsp"
    

    def get_variable_offset(self, name):
        if isinstance(name, StructMemberAccess):
            name = name.get_path()

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
        # TODO: Make this nicer and ideally part of the output logic
        for index in range(len(combined)):
            output = []
            lines = combined[index].split("\n")
            for i in lines:
                clean_text = re.sub(r"^\s+","", i)
                clean_text = re.sub(' +', ' ', clean_text)
                if not ":" in clean_text and not "." in clean_text:
                    clean_text = "\t" + clean_text
                output.append(clean_text)
            combined[index] = "\n".join(output)
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
            output.variable_2_type[node.name] = node.type
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
                            if "*" in str(node.type):
                                output.append(
                                    load_value(
                                        MemoryLocation(0, Register("rbx")),
                                        Register("rax"),
                                        output,
                                    ),
                                    comment="Temp storage to speed it all up (reference)"
                                )
                            else:
                                output.append(
                                    load_value(
                                        MemoryLocation(0, Register("rbx")),
                                        Register("rax"),
                                        output,
                                    ),
                                    comment="Temp storage to speed it all up (dereference)"
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
                                comment="Load value into rax"
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
                        output.append(
                            f"\tmovl $0, %eax",
                            comment="I zero out after assignment"
                        )
                elif "struct" in node.type.name:
                    # For each member we allocate a variable ... bit hacky, but works for now
                    if "*" in node.type.name:
                        # We just load the pointer
                        output.append(
                            load_value(
                                NumericValue(0),
                                PushLocation(node.name),
                                output,
                            ),
                            comment="Load struct pointer"
                        )
                        raise Exception("huh")
                    else:
                        members =  self.ast.global_types[node.type.name.split("struct ")[-1]]
                        for i in members.members:
                            output.append(
                                load_value(
                                    NumericValue(0),
                                    PushLocation(node.name + "." + i.name),
                                    output,
                                ),
                                comment="Load struct member " + str(i)
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
                reference_stack = self.get_stack_variable_value(node.expr_1.variable, output)
                output.append(f"\taddl $1, {reference_stack}", comment="Add the ++ to the reference stack")
            else:
                raise Exception("what is this? I don't know this op in binary op")
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
                elif isinstance(node.v_reference, StructMemberDereferenceAccess):
                    _ = self.get_struct_member_load(node.v_reference, node.value, output)
                    # TODO: Fix this 
                    if isinstance(node.value, NumericValue):
                        output.append(
                            load_value(
                                node.value,
                                MemoryLocation(0, Register("rbx")),
                                output,
                            ),
                            comment=f"Load variable ({node.value}) into memory location"
                        )                    
                    else:
                        output.append(
                            load_value(
                                StackLocation(self.get_stack_variable_offset(node.value.variable, output)),
                                MemoryLocation(0, Register("rbx")),
                                output,
                            ),
                            comment=f"Load variable ({node.value.variable}) into memory location"
                        )
                else:
                    reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                    output.append(
                        f"\tmovl ${node.value.value}, {reference_stack}"
                    )
            elif isinstance(node.value, VariableReference):
                """
                TODO: Refactor all of this code section
                """
                if isinstance(node.v_reference, StructMemberDereferenceAccess):
                    _ = self.get_struct_member_load(node.v_reference, node.value.variable, output)
                    # load the variable value
                    output.append(
                        load_value(
                            StackLocation(self.get_stack_variable_offset(node.value.variable, output)),
                            Register("rdx"),
                            output,
                        ),
                        comment=f"Load variable ({node.value.variable}) into memory location of reference"
                    )
                    output.append(
                        load_value(
                            Register("rdx"),
                            MemoryLocation(0, Register("rbx")),
                            output,
                        ),
                        comment=f"Load value into rbx offset"
                    )
                elif isinstance(node.value, VariableReference) and isinstance(node.value.variable, StructMemberDereferenceAccess):
                    member_access = self.get_struct_member_load(node.value.variable, output)
                    output.append(
                        f"mov %rbx, {member_access}",
                        comment=f"Load variable ({node.value.variable}) into memory location"
                    )
                else:
                    output.append(
                        load_value(
                            StackLocation(self.get_stack_variable_offset(node.value.variable, output)),
                            Register("ebx"),
                            output,
                        ),
                        comment=f"Load value({node.value.variable}) before assignment"
                    )
                    output.append(
                        load_value(
                            Register("ebx"),
                            VariableLocation.from_variable_name(node.v_reference, self.ast, output),
                            output,
                        ),
                        comment=f"Use loaded value for assignment ({node.v_reference})"
                    )
            else:
                output.append(
                    f"\txor %rax, %rax",
                    comment="I zero out after assignment"
                )
                # In the case of function calls etc
                self.convert_nodes(node.value, output)
                reference_stack = output.get_or_set_stack_location(node.v_reference, None)
                output.append(
                    f"\tmov %rax, {reference_stack}",
                    comment=f"Set the node result into variable {node.v_reference}"
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
                if len(node.parameters.child_nodes) != len(self.ast.functions[node.function_name].parameters.child_nodes):
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
                    f"\tcall {node.function_name}@PLT"
                )
                # Now we need to clear the fields ... 
                if len(node.parameters.child_nodes):
                    stack = len(node.parameters.child_nodes) * 8
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
                reference_stack = self.get_stack_variable_value(node.a.variable, output)
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
            # Need to check this and then jump ...
            self.convert_nodes(node.initialization_statement, output)
            output.append(f"jmp loop{node.id}")
            # Jump to the conditional
            output.append(f"cloop{node.id}:")
            # Parse the body data
            self.convert_nodes(node.body, output)
            self.convert_nodes(node.update_statement, output)
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
            reference_stack = self.get_stack_variable_value(node.variable, output)
            output.append(f"\taddl {reference_stack}, %eax", comment="Add the reference stack")
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

    def is_variable_function_parameter(self, variable):
        parameter_index = -1 # 
        for index, i in enumerate(self.current_function.parameters.child_nodes):
            if i.name == variable:
                parameter_index = index
                break
        return parameter_index
    
    def get_struct_member_index(self, node: StructMemberDereferenceAccess, output: AsmOutputStream):
        index = -1
        variable = output.variable_2_type.get(
            node.variable_reference,
            self.ast.global_variables.get(node.variable_reference, None)
        )
        if variable is None:
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
        variable = VariableLocation.from_variable_name(node.variable_reference, self.ast, output)
        member_access = StackLocation(self.get_stack_variable_offset(node.variable_reference, output))
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
            comment=f"Load variable ({field_name}) reference into rbx"
        )
        if index != -1:
            if index != 0:
                #raise Exception("Need to adjust the pointer location for the size")                           
                output.append(f"add ${index * 8}, %rbx")
            return member_access
        else:
            raise Ellipsis("Did not find the struct variable location")
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
    def from_variable_address_reference(variable: str, output: AsmOutputStream):
        # Find the place in memory that the variable is store so loading is simple
        return VariableLocation(output.get_memory_offset(variable))
    
    @staticmethod
    def from_variable_name(variable: str, ast: File, output: AsmOutputStream):
        if variable in ast.global_variables:
            return VariableLocation.from_global_variable(variable)
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
