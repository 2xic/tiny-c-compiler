struct TestStruct
{
    int myNum1;
    int myNum2;
};


struct TestStruct *globalValue;

int main(){
    struct TestStruct value; // Push the two items onto the stack
    value.myNum1 = 2;        // Assign item 1

    /**Noise to move around the pointers */
    struct TestStruct value2; // Push the two items onto the stack
    value2.myNum1 = 2;        // Assign item 1

    struct TestStruct *temp = &value;

    globalValue = temp;

    globalValue->myNum1 = 92;

    return value.myNum1;

}
