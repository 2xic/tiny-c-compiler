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

    int sizeBeforeAllocation = brk(0);

    int *b = malloc(5);
    *b = 9;
    
    if (b == -1){
        return 1;
    }

    free(b);

    int sizAfterFree = brk(0);

    int delta = sizeBeforeAllocation - sizAfterFree;

    int size = getSize() + delta;

    return size;
}

