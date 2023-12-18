/**
 * How we want to implement this
 * - Int takes 8 bytes
 * - Structs takes n bytes
 * 
 * 1. We allocate on the stack and will only support function scope to starts with
 * 2. ast_2_asm needs to keep track of sizes of the variables on the stack
 * 3.  
*/
struct TestStruct
{
    int myNum1;
    int myNum2;
};

int main()
{
    struct TestStruct value;
    value.myNum1 = 2;
    value.myNum2 = value.myNum1 + value.myNum2;

    return value.myNum2;
}
