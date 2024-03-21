
int main(){
    int a = 4;

    int *p = &a; // copy the pointer location of a

    *p = 9; // dereference the pointer location of a and assign to the address

    return a;
}
