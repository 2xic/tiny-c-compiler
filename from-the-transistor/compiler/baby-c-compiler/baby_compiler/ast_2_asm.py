"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall


class AsmOutputStream:
    def __init__(self, name) -> None:
        self.name = name
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

    def append(self, text):
        self.output_stream.append(text)

def create_sys_exit(exit_code):
    if isinstance(exit_code, NumericValue):
        return f"""
    movl    ${exit_code}, %ebx
    movl    $1, %eax
    int     $0x80
        """
    else:
        # Hm - not ideal way to implement this but works
        return f"""
    movl    {exit_code}, %ebx
    movl    $1, %eax
    int     $0x80
        """

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
        for i in self.ast.functions:
            if i != "main":
                function_code = AsmOutputStream(
                    name=i
                )
                self.convert_nodes(self.ast.functions[i], function_code)
                print(self.ast.functions[i], function_code.output_stream)
                other_functions += function_code.output_stream


        # Need to insert one new lien at the end else the compiler is mad
        combined = main_function_output.output_stream + other_functions + self.data_sections
        return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(combined).split("\n")))) + "\n"

    def convert_nodes(self, node, output: AsmOutputStream):
        print(node)
        if isinstance(node, File):
            return self.convert_nodes(node, output)
        elif isinstance(node, FunctionDefinition):
            return self.convert_nodes(node.body, output)
        elif isinstance(node, VariableDeclaration):
            # TODO: Doing this just because it is easier to deal with
            # Likely we should do some stack allocations etc depending on context 
            if isinstance(node.value, MathOp):
                self.data_sections.append(
                    f"\t{node.name}: .word 0"
                )
                # THen we store this into the .data value ? 
                output.append(
                    f"\txor %eax, %eax"
                )
                self.convert_nodes(node.value, output) 
                output.append(
                    f"\tmovl %eax, {node.name}"
                )
            elif node.value is None:
                self.data_sections.append(
                    f"\t{node.name}: .word 0"
                )
            elif isinstance(node.value, FunctionCall):
                output.append(
                    f"\tcall {node.value.function_name}"
                )
                print("swap?")
            else:
                self.data_sections.append(
                    f"\t{node.name}: .word {node.value}"
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
                    output.append(create_sys_exit("eax"))
                else:
                    output.append(create_sys_exit(node.value))
            else:
                output.append("\tpushq   %rbp")
                if isinstance(node.value, NumericValue):
                    # We return a static value ? 
                    # okay 
                    output.append(f"\tmovl    ${node.value}, %eax")
                elif isinstance(node.value, MathOp):
                    self.convert_nodes(node.value, output)
                
                output.append("\tpopq    %rbp")
                output.append("\tret")

        elif isinstance(node, MathOp):
            """
            The add opcode from assembly is like this
            ADD immediate value to a register
            """
            # We write to EAX, but should be able to do more dynamic allocations soonish
            if isinstance(node.expr_1, FunctionCall):
                output.append("\tmovl %eax, %ebx") # copy over the value
                self.convert_nodes(node.expr_1, output)
                output.append(
                    f"\taddl %ebx, %eax"
                )
            elif isinstance(node.expr_1, NumericValue):
                output.append(f"\taddl ${node.expr_1}, %eax")
            else:
                raise Exception("Unknown mathop tree")
            # expr -2
            if isinstance(node.expr_2, NumericValue):
                output.append(f"\taddl ${node.expr_2}, %eax")
            elif isinstance(node.expr_2, MathOp):
                self.convert_nodes(node.expr_2, output)                
            elif isinstance(node.expr_2, FunctionCall):
                output.append("\tmovl %eax, %ebx") # copy over the value
                self.convert_nodes(node.expr_2, output)
                output.append(
                    f"\taddl %ebx, %eax"
                )
                # Now we can restore it 
                # We now need to deal with the restoring of the value 
            else:
                raise Exception(f"Unknown math op node ({node})")

        elif isinstance(node, VariableAssignment):
            if isinstance(node.v_value, NumericValue):
                output.append(
                    f"\tmovl ${node.v_value.value}, {node.v_reference}"
                )
            elif isinstance(node.v_value, MathOp):
                self.convert_nodes(node.v_value, output)
                output.append(
                    f"\tmovl %eax, {node.v_reference}"
                )
            elif isinstance(node.v_value, FunctionCall):
               output.append(
                    f"\tcall {node.v_value.function_name}"
                )
                # do the call ... we store the results in registers ? or stack ?                 
               output.append(
                    f"\tmovl %eax, {node.v_reference}"
               )
            else:
                raise Exception("I did not implement math expressions here yet")
        elif isinstance(node, FunctionCall):
               output.append(
                    f"\tcall {node.function_name}"
                )
        else:
            raise Exception("Unknown node " + str(node))    
