// Define it for the linker
int *sbrk(int increment);

int main(){
    int *a = sbrk(5);
    *a = 5;

    if (a == -1){
        return 1;
    }
    return a;
}
