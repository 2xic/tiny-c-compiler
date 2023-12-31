// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);

int main(){
    int *a = malloc(5);
    if (a == -1){
        return 1;
    }

    // Write the value
    int *c = a;
    for(int i = 0; i < 5; i++){
        *c = i;
        c++;
    }

    // Read in the value again
    int sum = 0;
    int *d = a;
    for(int i = 0; i < 5; i++){
        int val = *d;
        sum = sum + val;
        d++;
    }

    return sum;
}
