

int adjustPointer(int b){
    int a = 9;

    if (b != 4){
        return 2;
    }

    return a;
}

int main(){
    int a = 4;

    int c = adjustPointer(5);

    return a + c;
}
