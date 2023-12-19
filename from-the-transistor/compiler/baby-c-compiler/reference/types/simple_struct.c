struct TestStruct
{
    int myNum1;
    int myNum2;
};

int main()
{
    struct TestStruct value; // Push the two items onto the stack
    value.myNum1 = 2;        // Assign item 1

    return value.myNum1;
}
