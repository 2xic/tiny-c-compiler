// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);
int memcpy(int *from_address, int *to_address, int size);

int main()
{
    int *a = malloc(5);
    if (a == -1)
    {
        return 1;
    }

    int *b = malloc(5);

    // Write the value
    int *c = a;
    for (int i = 0; i < 5; i++)
    {
        *c = i;
        c++;
    }

    // Here memcpy depends on the variable
    int *pp = a;
    int *dd = b;
    memcpy(pp, dd, 5);

    // Read in the value again
    int sum = 0;
    int *valuePointer = dd;
    for (int i = 0; i < 5; i++)
    {
        int val = *valuePointer;
        sum = sum + val;
        valuePointer++;
    }

    return sum;
}
