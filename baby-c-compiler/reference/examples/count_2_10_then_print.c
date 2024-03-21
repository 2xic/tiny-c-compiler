

int printDone(int *c){
    write(1, 1, "done\n");

    *c = 10;

    return 5;
}

int main(){
    int a = 4;
    int b = 0;
    int c = 0;
    int *p = &c;

    while(a == 4) {
        b = b + 1;

        if (b == 10) {
            a = 0;
        }

        write(1, 1, "counting\n");
    }

    if (a == 0){
        b = printDone(p);
    }

    return b + c; // returns 15
}
