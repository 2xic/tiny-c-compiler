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
            self.data_sections.append(
                f"\t{node.name}: .word 0"
            )
            if not node.value is None:
                # Else the node has to write the data to %eax at some point during the evaluation
                self.convert_nodes(node.value, output) 
                output.append(
                    f"\tmovl %eax, {node.name}"
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
            # We write to EAX, but should be able to do more dynamic allocations soon
            self.handle_math_opcodes(node.expr_1, output)
            self.handle_math_opcodes(node.expr_2, output)

        elif isinstance(node, VariableAssignment):
            # This should also zero out eax ....
            # ^ technically I think we should zero eax at a different point, but okay
            output.append(
                f"\tmovl $0, {node.v_reference}"
            )
            output.append(
                f"\tmovl $0, %eax"
            )
            # do the math
            if isinstance(node.value, NumericValue):
                output.append(
                    f"\tmovl ${node.value.value}, {node.v_reference}"
                )
            else:
                self.convert_nodes(node.value, output)
                output.append(
                    f"\tmovl %eax, {node.v_reference}"
                )
        elif isinstance(node, FunctionCall):
               output.append(
                    f"\tcall {node.function_name}"
                )
        else:
            raise Exception("Unknown node " + str(node))    
    
    def handle_math_opcodes(self, node, output):
        if isinstance(node, NumericValue):
            output.append(f"\taddl ${node}, %eax")
        elif isinstance(node, MathOp):
            self.convert_nodes(node, output)                
        elif isinstance(node, FunctionCall):
            self.backup_eax_then_add_restore(node, output)
        else:
            raise Exception(f"Unknown math op node ({node})")
        
    def backup_eax_then_add_restore(self, node, output):
        output.append("\tmovl %eax, %ebx") # copy over the value
        self.convert_nodes(node, output)
        output.append(
            f"\taddl %ebx, %eax"
        )
