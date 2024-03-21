
int main(){
    int a = 4;

    int *p = &a; // copy the pointer location of a

    int c = 12;

    *p = 9; // dereference the pointer location of a and assign to the address

    return a;
}
