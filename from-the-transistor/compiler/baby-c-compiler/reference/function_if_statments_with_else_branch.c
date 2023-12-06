
int topLevelCall() {
    return 5;
}

int main(){
    int a = topLevelCall();

    if (a == 9){
        // Then we write
        write(1, 1, "yes");
    } else {
        write(1, 1, "No");
        a = 3;
    }

    return a;
}
