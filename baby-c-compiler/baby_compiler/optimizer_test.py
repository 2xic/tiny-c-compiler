"""
There should be a way for us to go from the AST nodes back into C code also ...

Just because of helping e2e tests and also source modifications.


"""
from .compiler import get_ast
from .ast_2_c import Ast2C
from .optimizer import Optimizer

def _raw_encode(source_code):
    file = get_ast(source_code).build_ast()
    return file

def test_1():
    source_code = """
    int main(){
        int a = 2 + 2;
        return a;
    }
    """
    file = _raw_encode(source_code)
    optimized = Optimizer().process(file)
    remade_into_c = Ast2C(optimized).get_source_code()

    # Very optimized source code ....
    # Could even replace the a ....
    # Second pass of the optimizer ofc.
    optimized_source_code = """
    int main(){
        int a = 4;
        return a;
    }
    """
    file = _raw_encode(optimized_source_code)
    optimized_source_standardized = Ast2C(file).get_source_code()
    assert remade_into_c == optimized_source_standardized

if __name__ == "__main__":
    test_1()
