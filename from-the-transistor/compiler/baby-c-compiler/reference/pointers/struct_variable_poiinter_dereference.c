struct TestStruct
{
    int myNum1;
    struct memory_blocks *next; // 8
    int myNum2;
};


struct TestStruct *globalValue;

int main(){
    struct TestStruct value; 
    value.myNum1 = 2;
    value.next = 0;

    int a = 0;

    struct TestStruct *p = &value; // Pointer of p (should be the stack memory address)

    p->myNum2 = 8;

    int sum = p->myNum2;

    return sum;
}
