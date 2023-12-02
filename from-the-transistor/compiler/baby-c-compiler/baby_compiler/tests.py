"""
Messy tests, lalalala
"""

from .ast import Tokenizer, AST
from .snapshots import Snapshot
from .ast_2_asm import Ast2Asm

tokenizer = Tokenizer(
    """
        int main(){
            return 2;
        }
    """
)
print(tokenizer.tokens)
assert Snapshot("correct_tokenized", tokenizer.tokens).check()

tree = AST(tokenizer.tokens)
file_ast = tree.build_ast()
assert Snapshot("ast", str(file_ast)).check()

asm = Ast2Asm(file_ast)
assert Snapshot("asm", str(asm.get_asm())).check()

