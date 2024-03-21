

int adjustPointer(int *p, int c){
    int a = 4;
    int c = 0;

    *p = 9; // dereference the pointer location of a and assign to the address

    return 0;
}

int main(){
    int a = 4;

    int *p = &a; // copy the pointer location of a

    int c = adjustPointer(p, 0);

    return a + c;
}
