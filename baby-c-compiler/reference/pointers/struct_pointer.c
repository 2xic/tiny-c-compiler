struct TestStruct
{
    int myNum1;
    int myNum2;
};

int adjustTheValue(struct TestStruct *a){
    a->myNum1 = 2;
    return 2;
}

int main()
{
    struct TestStruct value; 
    struct TestStruct *p = &value;
    adjustTheValue(p);

    int results = value.myNum1;
    return results;
}
