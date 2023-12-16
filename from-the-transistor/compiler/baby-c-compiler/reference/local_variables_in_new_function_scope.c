

int adjustPointer(int *p){
    *p = 9; // dereference the pointer location of a and assign to the address

    int a = 4;

    return a;
}

int main(){
    int a = 4;

    int *p = &a; // copy the pointer location of a

    int c = adjustPointer(p);

    return a + c;
}
