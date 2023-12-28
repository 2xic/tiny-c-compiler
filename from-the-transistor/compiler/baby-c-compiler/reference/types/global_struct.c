struct TestStruct
{
    int myNum1;
    int myNum2;
};

struct TestStruct value; // Push the two items onto the stack

int main()
{
    value.myNum1 = 2;        // Assign item 1
    value.myNum2 = 4;        // Assign item 1

    int results = value.myNum1 + value.myNum2;

    return results;
}
