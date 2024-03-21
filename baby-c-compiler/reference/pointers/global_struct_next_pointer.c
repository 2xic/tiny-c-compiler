struct TestStruct
{
    int myNum1;
    struct memory_blocks *next; // 8
};


struct TestStruct *globalValue;

int main(){
    // This is pushed onto the stack
    struct TestStruct value; 
    value.myNum1 = 2;           // RSP - +0x24
    value.next = 42;             // RSP - 0x16

    int a = 0;                  // RSP  - 0x8

    struct TestStruct *p = &value; // RSP - Pointer of p (should be the stack memory address)

    while(p != 42){
        // P = Reference to RSP - 0x-16
        // Dereference P should point to start of value (currently it points at the end)
        // Then we add 8 to find the pointer value

        p = p->next; // (should dereference the stack pointer and add a 8 to the location)
        a++;
    }

    return a;
}
