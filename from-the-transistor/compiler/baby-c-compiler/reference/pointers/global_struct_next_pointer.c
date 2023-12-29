struct TestStruct
{
    int myNum1;
    struct memory_blocks *next; // 8
};


struct TestStruct *globalValue;

int main(){
    struct TestStruct value; 
    value.myNum1 = 2;
    value.next = 0;

    int a = 0;

    struct TestStruct *p = &value; // Pointer of p (should be the stack memory address)

    while(p != 0){
        p = p->next; // (should dereference the stack pointer and add a 8 to the location)
        a++;
    }

    return a;
}
