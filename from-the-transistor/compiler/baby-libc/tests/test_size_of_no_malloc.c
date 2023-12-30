// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);
int sumSize();
int getSize();

int main(){
    int size = sumSize() + getSize();

    return size;
}
