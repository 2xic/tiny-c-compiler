"""
Trying to make the struct logic simpler also
"""
from ..ast import StructMemberDereferenceAccess, VariableDeclaration, NumericValue
from .asm_output_stream import AsmOutputStream
from .memory_operations import VariableLocation, Register, load_value, PushLocation

class StructOperations:
    def __init__(self, ast, parameter_location) -> None:
        self.ast = ast
        self.parameter_location = parameter_location

    """
    Struct member accesses
    """
    def get_struct_member_load(self, node: StructMemberDereferenceAccess, output: AsmOutputStream):
        """
        RBX 
        """
        variable = VariableLocation.from_variable_name(node.variable_reference, self.parameter_location, self.ast, output)
        member_access =  VariableLocation.from_variable_name(
            node.variable_reference, self.parameter_location, self.ast, output
        )
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
            comment=f"Load variable ({node.value}) reference into rbx from {member_access}"
        )
        if index != -1:
            if index != 0:
                # [struct_member_1, struct_member_2]
                    # 0xff
                    # 0xf7
                # We need to access the lower item
                output.append(f"add ${index * 8}, %rbx", comment=f"Access of {node.value} on {node.variable_reference}")
            else:
                output.append(f"", comment=f"Variable accessed was zero, no need to adjust the value {str(node)}")
            return member_access
        else:
            raise Ellipsis("Did not find the struct variable location")

    def get_struct_member_index(self, node: StructMemberDereferenceAccess, output: AsmOutputStream):
        variable = None

        # TODO: This is not a good way to implement this 
        if node.variable_reference in output.variable_2_type:
            variable = output.variable_2_type[node.variable_reference]
        elif node.variable_reference + "_" + node.value in self.ast.global_variables:
            variable = self.ast.global_variables[node.variable_reference + "_" + node.value]
        elif node.variable_reference in self.ast.global_variables:
            variable = self.ast.global_variables[node.variable_reference]
        elif node.variable_reference in self.parameter_location.parameter_names:
            variable = self.parameter_location.get_variable(node.variable_reference)

        if variable is None:
            raise Exception("I did not find the variable reference")

        if isinstance(variable, VariableDeclaration):
            variable = variable.type
        # Find the struct member index
        index = -1
        name = variable.name.replace("*","").split(" ")[-1]
        for member_i, i in enumerate(self.ast.global_types[name].members):
            if i.name == node.value:
                index = member_i
                break
        return index


    def put_struct_members_on_stack(self, type_name, node: VariableDeclaration, output: AsmOutputStream):
        # For each member we allocate a variable ... bit hacky, but works for now
        if "*" in type_name:
            # We just load the pointer
            raise Exception("huh")
        else:
            # TODO: clean this up
            members = self.ast.global_types[type_name.split("struct ")[-1]]
            for i in list(reversed(members.members)):
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
