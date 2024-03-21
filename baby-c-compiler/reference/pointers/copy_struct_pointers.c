struct TestStruct
{
    int myNum1;
    int myNum2;
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

    struct TestStruct *temp = &value;
                            // Should reference the first stack entry 

    globalValue = temp;

    globalValue->myNum1 = 92;

    return value.myNum1;

}
