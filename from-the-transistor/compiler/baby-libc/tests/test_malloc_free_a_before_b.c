// Define it for the linker
int *malloc(int increment);
int free(int *a);
int getSize();

int main()
{
    int *a = malloc(5);
    *a = 9;

    if (a == -1)
    {
        return 1;
    }

    // This should trigger a new allocation at the end of previous segment
    int *b = malloc(5);
    if (b == 1)
    {
        return 1;
    }
    *b = 9;

    int p = *b; // This should dereference the B value ... ?

    // This should be okay as the library should correctly not adjust the program segment before b is also freed :)
    free(a);

    free(b);

    int size = getSize();

    int sum = size + p;

    return sum;
}
