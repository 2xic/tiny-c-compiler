"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp


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
            """
.text
    .global _start
_start:
            """
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
        self.convert_nodes(self.ast.functions["main"])
        # Need to insert one new lien at the end else the compiler is mad
        combined = self.output_asm + self.data_sections
        return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(combined).split("\n")))) + "\n"

    def convert_nodes(self, node):
        if isinstance(node, File):
            return self.convert_nodes(node)
        elif isinstance(node, FunctionDefinition):
            return self.convert_nodes(node.body)
        elif isinstance(node, VariableDeclaration):
            # TODO: Doing this just because it is easier to deal with
            # Likely we should do some stack allocations etc depending on context 
            if isinstance(node.value, MathOp):
                self.data_sections.append(
                    f"\t{node.name}: .word 0"
                )
                # THen we store this into the .data value ? 
                self.output_asm.append(
                    f"\t\txor %eax, %eax"
                )
                self.convert_nodes(node.value) 
                self.output_asm.append(
                    f"\t\tmovl %eax, {node.name}"
                )
            else:
                self.data_sections.append(
                    f"\t{node.name}: .word {node.value}"
                )
        elif isinstance(node, FunctionBody):
            for i in node.child_nodes:
                self.convert_nodes(i)
        elif isinstance(node, ReturnDefinition):
            # technically it should only be a exit if this is the main opcode ...
            if isinstance(node.value, MathOp):
                # Unwrap it ... push add push add ..
                # We will store the results into memory ...
                self.convert_nodes(node.value)
                self.output_asm.append(create_sys_exit("eax"))
            else:
                self.output_asm.append(create_sys_exit(node.value))
        elif isinstance(node, MathOp):
            """
            The add opcode from assembly is like this
            ADD immediate value to a register
            """
            # We write to EAX
            self.output_asm.append(f"\t\taddl ${node.expr_1}, %eax")
            if isinstance(node.expr_2, NumericValue):
                self.output_asm.append(f"\t\taddl ${node.expr_2}, %eax")
            else:
                self.convert_nodes(node.expr_2)            
        else:
           
            raise Exception("Unknown node " + str(node))    


