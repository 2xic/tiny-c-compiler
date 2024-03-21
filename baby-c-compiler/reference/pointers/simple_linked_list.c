struct TestStruct
{
    struct TestStruct *next;
    int myNum1;
};


struct TestStruct *globalValue;

int main(){
    struct TestStruct value; // Push the two items onto the stack
    value.myNum1 = 2;        // Assign item 1
                             // First stack entry

    /**Noise to move around the pointers */
    struct TestStruct value2; // Push the two items onto the stack
    value2.myNum1 = 2;        // Assign item 1
                             // Second stack entry

    struct TestStruct *value2Pointer = &value2;
    struct TestStruct *value1Pointer = &value;

    globalValue = value1Pointer;

    globalValue->next = value2Pointer;
    value2Pointer->next = 0;

    int a = 0;
    struct TestStruct *p = &value; // Push the two items onto the stack
    while(p != 0){
        p = p->next;
        a++;
    }

    return a;
}
