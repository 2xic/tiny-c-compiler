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

    int size = getSize();

    return size;
}
