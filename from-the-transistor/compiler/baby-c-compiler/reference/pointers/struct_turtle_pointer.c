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
    value.next = 0;             // RSP - 0x16

    struct TestStruct *turtle = &value; // RSP - Pointer of p (should be the stack memory address)
    int a = 0;

    while(a == 0){        
        struct memory_blocks *current = turtle->next;
        if (current == 0){
            a = 1;
        } else {
            // This should assign to the turtle .... 
            turtle = turtle->next;
        }
    }

    // Turtle value == 2
    int numValue = turtle->myNum1;

    return numValue;
}
