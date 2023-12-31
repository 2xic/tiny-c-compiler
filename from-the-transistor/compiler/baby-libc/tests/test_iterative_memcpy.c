// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);

int main(){
    int *a = malloc(5);
    if (a == -1){
        return 1;
    }

    int *c = a;
    *c = 5;
    c++;
    *c = 10;

    // Sum the sum (with 5 we should have 0 + 1 + 2 + 3 + 4 == 10)
    int sum = 0;
    int *d = a;
    int first = *d;
    d++;
    int second = *d;
    sum = first + second;

    return sum;
}
