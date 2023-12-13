/**
 * We don't store global variables on the stack, but keep them in the .data section.
*/


int A = 2;

int main(){
    return A;
}
