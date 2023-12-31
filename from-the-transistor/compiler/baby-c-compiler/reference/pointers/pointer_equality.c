

int main(){
    int value = 42;

    int *v = &value;
    int *p = v;


    if (v == p){
        return 1;
    } else {
        return 0;
    }
}
