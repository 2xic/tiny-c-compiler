struct TestStruct
{
    int myNum1;
    int myNum2;
};

int main()
{
    struct TestStruct value; 
    value.myNum1 = 2;        
    value.myNum2 = value.myNum1 + value.myNum1; 

    struct TestStruct value2; 
    value2.myNum1 = value.myNum2 + 1;
    value2.myNum2 = value.myNum1 + 1;

    return value2.myNum1 + value2.myNum2;
}
