
int topLevelCall() {
    return 9;
}

int main(){
    int a = topLevelCall();

    if (a == 9){
        // Then we write
        write(1, 1, "yes");
    } else {
        write(1, 1, "No");
    }

    return 0;
}
