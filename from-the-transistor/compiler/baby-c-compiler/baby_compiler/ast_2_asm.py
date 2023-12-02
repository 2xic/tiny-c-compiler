"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition


def create_sys_exit(exit_code):
    return f"""
    movl    ${exit_code}, %ebx
    movl    $1, %eax
    int     $0x80
    """

class Ast2Asm:
    def __init__(self, ast: File) -> None:
        self.ast = ast
        self.output_asm = [
            """
.text
    .global _start
_start:
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
        return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(self.output_asm).split("\n")))) + "\n"

    def convert_nodes(self, node):
        if isinstance(node, File):
            return self.convert_nodes(node)
        elif isinstance(node, FunctionDefinition):
            return self.convert_nodes(node.body)
        elif isinstance(node, ReturnDefinition):
            # technically it should only be a exit if this is the main opcode ...
            self.output_asm.append(create_sys_exit(node.value))
        else:
            raise Exception("Unknown node " + str(node))    


