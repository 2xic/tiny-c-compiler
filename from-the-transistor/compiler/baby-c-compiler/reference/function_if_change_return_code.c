
int topLevelCall() {
    return 9;
}

int main(){
    int a = topLevelCall();

    if (a == 9){
        // Then we write
        a = 4;
    } else {
        write(1, 1, "No");
        a = 10;
    }

    return a;
}
