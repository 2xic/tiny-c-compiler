// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);
int getSize();

int main(){
    int sizeBeforeAllocation = brk(0);

    int *a = malloc(5);
    *a = 9;
    
    if (a == -1){
        return 1;
    }

    int *b = malloc(5);
    *b = 9;
    
    if (b == -1){
        return 1;
    }

    free(b);
    free(a);

    int sizAfterFree = brk(0);
    
    int delta = sizeBeforeAllocation - sizAfterFree;
    int size = getSize();

    int sum = size + delta;

    if (sum == 0){
        return 0;
    } else {
        return sum;
    }
}
