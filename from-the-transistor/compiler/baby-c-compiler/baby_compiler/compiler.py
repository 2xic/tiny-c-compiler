import sys
from .ast import Tokenizer, AST
from .ast_2_asm import Ast2Asm
from .exceptions import InvalidSyntax

def compile(file):
    tokenizer = Tokenizer(
        file
    )

    tree = AST(tokenizer.tokens)
    try:
        file_ast = tree.build_ast()
        asm = Ast2Asm(file_ast) 
        return asm.get_asm()
    except InvalidSyntax as e:
        exit(-1)


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, "r") as file:
        with open(output_file, "w") as write_file:
            write_file.write(compile(file.read()))
    exit(0)
