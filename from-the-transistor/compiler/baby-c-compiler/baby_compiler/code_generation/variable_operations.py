"""
So much of the code between the declaration and assignment of variables were duplicated instead of being shared.
"""
from ..ast import VariableAssignment, NumericValue, VariableAddressDereference, StructMemberDereferenceAccess, StructMemberAccess, VariableReference, VariableDeclaration, VariableAddressReference
from .memory_operations import Register, MemoryLocation, load_value, VariableLocation, StackLocation, PushLocation, ParameterLocation
from .asm_output_stream import AsmOutputStream
from .struct_operations import StructOperations
from ..exceptions import InvalidSyntax

class VariableOperations:
    def __init__(self, ast, parameter_location: ParameterLocation) -> None:
        self.ast = ast
        self.parameter_location = parameter_location

    def handle_declaration(self, node: VariableDeclaration, output: AsmOutputStream):
        output.variable_2_type[node.name] = node.type
        # TODO: Or in the function parameters
        if node.name in output.variables_stack_location:
            raise InvalidSyntax(f"Invalid - re-declaration of variable of {node.name}")
        if node.parent is None:
            # This is global variable so we store it in the .data section
            output.data_sections.append(
                f"\t{node.name}: .quad 0" # TODO: THis should likely be a long ?
            )
            if isinstance(node.value, NumericValue):
                output.append(
                    load_value(node.value, VariableLocation(node.name), output),
                    comment=f"{node.name} allocation"
                )
            elif node.value is not None:
                raise Exception("Unsupported global variable value")
        else:
            if node.value is not None:
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
                elif isinstance(node.value, VariableAddressDereference):
                    value = node.value.value.variable
                    output.append(
                        load_value(
                            MemoryLocation(0, VariableLocation.from_variable_address_reference(value, output)),
                            Register("rbx"),
                            output,
                        ),
                        comment=f"Load in the variable location ({value})"
                    )
                    output.append(
                        load_value(
                            MemoryLocation(0, Register("rbx")),
                            PushLocation(node.name),
                            output,
                        ),
                        comment=f"Dereference into the value ({node.name})"
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

                        _ = StructOperations(self.ast, self.parameter_location).get_struct_member_load(
                            node.value.variable,
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
                                VariableLocation.from_variable_name(node.value.variable, self.parameter_location, self.ast, output),
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
                        ),
                        comment=f"Allocation of variable ({node.value.variable.variable})"
                    )
                else:
                    # Failed as we need to load a sub node value
                    return True 
            elif "struct" in node.type.name:
                StructOperations(self.ast, self.parameter_location).put_struct_members_on_stack(
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

    def handle_assignment(self, node: VariableAssignment, output: AsmOutputStream):
        if isinstance(node.right_side, NumericValue):
            if isinstance(node.left_side, VariableAddressDereference):
                """
                This loads in the stack offset and adjust in rax

                The dereference then loads teh value into the memory location
                """
                if node.left_side.value.variable in self.ast.global_variables:
                    # Then we load the value
                    output.append(
                        f"\tmovl ${node.right_side.value}, ({node.left_side.value.variable})",
                        comment=f"Assign to memory location of the variable"
                    )
                else:
                    # Assign to the location of the variable
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
                _ = StructOperations(self.ast, self.parameter_location).get_struct_member_load(node.left_side, output)
                output.append(
                    load_value(
                        node.right_side,
                        MemoryLocation(0, Register("rbx")),
                        output,
                    ),
                    comment=f"Load variable ({node.right_side}) into memory location dereference"
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
                # TODO: This is not nice at all.
                if reference_stack is None:
                    # reference_stack = output.get_or_set_stack_location(node.left_side, None)
                    reference_stack = VariableLocation.from_variable_name(node.left_side, self.parameter_location, self.ast, output)
                    if "%" in str(reference_stack):
                        output.append(
                            f"\tmov ${node.right_side.value}, {reference_stack}"
                        )
                    else:
                        output.append(
                            f"\tmovl ${node.right_side.value}, {reference_stack}"
                        )
                else:
                    output.append(
                        f"\tmovl ${node.right_side.value}, {reference_stack}"
                    )
        elif isinstance(node.right_side, VariableAddressReference):
            output.append(
                load_value(
                    VariableLocation.from_variable_address_reference(node.right_side.variable.variable, output),
                    VariableLocation.from_variable_name(node.left_side, self.parameter_location, self.ast, output),
                    output,
                ),
                comment=f"Assignment of variable (&{node.right_side.variable.variable} to {node.left_side})"
            )
        elif isinstance(node.left_side, VariableAddressDereference):
            if isinstance(node.right_side, VariableReference):
                output.append("", comment=f"[Start variable assignment of ({node.right_side.variable} to *{node.left_side.value.variable})]")
                output.append(
                    load_value(
                        VariableLocation.from_variable_name(node.right_side.variable, self.parameter_location, self.ast, output),
                        Register("rbx"),
                        output,
                    ),
                    comment=f"Load in variable {node.right_side.variable}",
                )
                output.append(
                    load_value(
                        MemoryLocation(0, VariableLocation.from_variable_address_reference(node.left_side.value.variable, output)),
                        Register("rax"),
                        output,
                    ),
                    comment=f"Assign the loaded variable to memory {node.left_side.value.variable}",
                )
                output.append(
                    load_value(
                        Register("rbx"),
                        MemoryLocation(0, Register("rax")),
                        output,
                    ),
                    comment=f"Assign the loaded variable to memory {node.left_side.value.variable}",
                )
                output.append("", comment="[END of variable assignment]")
            else:
                raise Exception("UNKNOWN NODE SIR")
        elif isinstance(node.right_side, VariableAddressDereference):
            value = node.right_side.value.variable
            name = node.left_side

            output.append(
                load_value(
                    MemoryLocation(0, VariableLocation.from_variable_address_reference(value, output)),
                    Register("rbx"),
                    output,
                ),
                comment=f"Load in the variable location ({value})"
            )
            output.append(
                load_value(
                    MemoryLocation(0, Register("rbx")),
                    Register("rdx"),
                    output,
                ),
                comment=f"Dereference into the value ({name})"
            )
            output.append(
                load_value(
                    Register("rdx"),
                    VariableLocation.from_variable_name(name, self.parameter_location, self.ast, output),
                    output,
                ),
                comment=f"Dereference into the value ({name})"
            )
        elif isinstance(node.right_side, VariableReference):
            """
            TODO: Refactor all of this code section
            """
            if isinstance(node.left_side, StructMemberDereferenceAccess):
                _ = StructOperations(self.ast, self.parameter_location).get_struct_member_load(node.left_side, output)
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
                _ = StructOperations(self.ast, self.parameter_location).get_struct_member_load(
                    node.right_side.variable,
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
                        VariableLocation.from_variable_reference(node.left_side, output),
                        output,
                    ),
                    comment="Load in the value of the rbx"
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
            # Failed as we need to load a sub node value
            return True 

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

    """
    Call function node and load in eax
    """
    def load_in_call_node_results(self, variable: str, call_function, output: AsmOutputStream):
        output.append(
            f"\txor %rax, %rax",
            comment="I zero out after assignment"
        )
        call_function()
        output.append(
            load_value(
                Register("eax"),    # TODO: This should be rax, but for some reason the address is off.
                VariableLocation.from_variable_reference(variable, output),
                output,
            ),
            comment=f"Set the node result into variable {variable}"
        )
        # We need to zero out rax after a function call
        output.append(
            f"\txor %rax, %rax",
            comment="I zero out after assignment"
        ) 
