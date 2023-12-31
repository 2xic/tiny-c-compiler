// Need to handle imports

// Put this into the PLT
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

    // This should be okay as the library should correctly not adjust the program segment before b is also freed :)
   free(a);

    // TODO: Now we can check if the program segment is changed ? 
  //  int p = *b; // This should dereference the B value ... ?

    free(b);

    int size = getSize();

    int sum = size;

    return sum;
}
