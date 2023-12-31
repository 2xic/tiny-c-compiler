
/**
 * With the c allocation
 * x/100 $rsp                           
 * 0x7fffffffde28: 0x401021        0x0     0x0     0x0
 * 0x7fffffffde38: 0xffffde58      0x7fff  0x0     0x0
 * 0x7fffffffde48: 0xffffde58      0x7fff  0xffffde58      0x7fff
 * 0x7fffffffde58: 0x4     0x0     0x1     0x0
 * 
 * Without the c allocation (correctly allocates the values on the stack)
 * 0x7fffffffde30: 0x40101b        0x0     0xffffde58      0x7fff
 * 0x7fffffffde40: 0xffffde58      0x7fff  0xffffde58      0x7fff
 * 0x7fffffffde50: 0xffffde58      0x7fff  0x4     0x0
 * 
 * 
*/
int callWithPointer(int *pv, int *vv){
    if (pv == vv){
        return 1;
    }

    return 0;
}

int main(){
    int a = 4; 

    int *p = &a; // copy the pointer location of a
    
    int *v = p;

    int c = callWithPointer(p, v); // This c call messes up the stack ?

    return c;
}
