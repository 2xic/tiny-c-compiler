// Define it for the linker
int *malloc(int increment);
int free(int *a);
int sumSize();
int getSize();

int main(){
    int *p = malloc(10);
    free(p);

    int size =  getSize();

    return size;
}
