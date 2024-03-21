// Define it for the linker
int *malloc(int increment);
int free(int *a);
int getSize();

int main(){
    int *a = malloc(5);
    *a = 9;

    if (a == -1){
        return 1;
    }

    // This should trigger a new allocation at the end of previous segment
    int *b = malloc(5);
    if (b == 1){
        return 1;
    }
    *b = 9;


    int p = *b; // This should dereference the B value ... ?

    free(b);

    // This should be okay as the library should correctly not adjust the program segment before b is also freed :)
    free(a);

    int size = getSize();

    int programSegment = brk(0);

    int *c = malloc(5);
    int *d = malloc(5);

    int programSegmentAfterMalloc = brk(0);

    int delta = programSegmentAfterMalloc - programSegment;

    // Then we allocate more variables ... THis should'nt change the size of the program segment

    int sum = size + p + delta;


    return sum;
}
