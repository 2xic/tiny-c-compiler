// Define it for the linker
int *malloc(int increment);
int free(int *a);

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

    // TODO: Now we can check if the program segment is changed ? 
    int p = *a;

    free(b);
    free(a);

    return p;
}
