
int main(){
    int a = 4;

    int *p = &a; 

    int *v = p;

    *v = 9; // dereference the pointer location of a and assign to the address

    return a;
}
