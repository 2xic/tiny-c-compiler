// Need to handle imports

// Put this into the PLT
int *sbrk(int increment);

int main(){
    int *a = sbrk(5);
    if (a == -1){
        return 1;
    }
    return a;
}
