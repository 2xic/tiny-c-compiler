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


def test_error_detection():
    """
    Example cases where the ast should get mad
    - Functions that are not defined
    - Variables that are not defined
    
    """
    pass


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
    source_code_test(
        """
            int main(){
                int a;
                a = 9 + 2;
                return a; // This should be a variable declaration :)
            }
        """
    )
    source_code_test(
        """
            int anotherFunction (){
                return 5;
            }

            int main(){
                int a = anotherFunction();
                return a;
            }
        """
    )
    source_code_test(
        """
            int thisIsOneMoreFunctions (){
                return 5;
            }

            int anotherFunction (){
                return 5 + thisIsOneMoreFunctions();
            }

            int main(){
                int a;
                a = anotherFunction();
                return a;
            }
        """
    )
