// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);
int getSize();
int sumSize();
int sumFree();

int main(){
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

    int *c = malloc(5);
    *c = 9;
    
    if (c == -1){
        return 1;
    }

    int size = getSize() + sumFree() + sumSize();

    return size;
}
