

struct value
{
    int num1;
    int num2;
};

int main()
{
    struct value struct_value;
    struct_value.num1 = 10;
    struct_value.num2 = 30;

    int a = 5;
    int *p = &a;
    p = &a; // Reassign the pointer

    *p = 12;

    int c = struct_value.num1;
    c = struct_value.num1;

    struct value *struct_pointer = &struct_value;

    int d = struct_pointer->num2;

    int e = struct_pointer->num1;

    int f;
    f = *p;
  
    int sum = a + c + d + e + f;

    return sum;
}
