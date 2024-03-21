

struct value
{
    int num1;
};

int main()
{
    struct value struct_value;
    struct_value.num1 = 10;

    int a = 5;
    int *p = &a;
    p = &a; // Reassign the pointer

    *p = 10;

    int c = struct_value.num1;
    c = struct_value.num1;

    struct value *struct_pointer = &struct_value;

    int d = struct_pointer->num1;

    int sum = a + c + d;

    return sum;
}
