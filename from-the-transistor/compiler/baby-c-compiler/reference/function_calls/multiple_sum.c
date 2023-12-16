
int thisIsOneMoreFunctions (){
    return 9;
}

int anotherFunction (){
    return 5 + thisIsOneMoreFunctions();
}

int main(){
    int a;
    a = anotherFunction();
    return a;
}
