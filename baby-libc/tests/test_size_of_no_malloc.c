// Define it for the linker
int *malloc(int increment);
int free(int *a);
int sumSize();
int getSize();

int main(){
    int size = sumSize() + getSize();

    return size;
}
