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
    
    return value.myNum1 + value.myNum2;
}
