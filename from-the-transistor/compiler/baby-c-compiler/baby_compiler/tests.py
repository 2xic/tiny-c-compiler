"""
Messy tests, lalalala
"""
import hashlib
from .ast import Tokenizer, AST
from .snapshots import Snapshot
from .ast_2_asm import Ast2Asm

def source_code_test(source_code):
    id_hash = hashlib.sha256(source_code.encode()).hexdigest()[:8]
    tokenizer = Tokenizer(source_code)
    print(tokenizer.tokens)
    assert Snapshot(f"{id_hash}_correct_tokenized", tokenizer.tokens).check()

    tree = AST(tokenizer.tokens)
    file_ast = tree.build_ast()
    assert Snapshot(f"{id_hash}_ast", str(file_ast)).check()

    asm = Ast2Asm(file_ast)
    assert Snapshot(f"{id_hash}_asm", str(asm.get_asm())).check()

if __name__ == "__main__":
    source_code_test(
        """
            /* Test */
            int main(){
                return 2;
            }
        """
    )
    source_code_test(
        """
            // Test 
            int main(){
                int a = 2;
                return 2;
            }
        """
    )
    source_code_test(
        """
            // Test 
            int main(){
                int a = 2 + 2 + 2 + 2; // This should not be evaluated in memory ...
                return a; // This should be a variable declaration :)
            }
        """
    )
