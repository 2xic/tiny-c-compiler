

int adjustPointer(int *p, int b){
    int a = 0;
    int c = 0;

    if (b == 5){
        *p = 9; // dereference the pointer location of a and assign to the address
    }

    return c;
}

int main(){
    int a = 4;

    int *p = &a; // copy the pointer location of a

    int c = adjustPointer(p, 5); // should trigger the overwrite of a = 9 and return 0

    return a + c; // result should be 9
}
