int func(){
    int a = 2;
    if (a == 9){
        int b = 2;
        return b;
    } else {
        return a;
    }
}

int main(){
    int b = func();

    return b;
}
