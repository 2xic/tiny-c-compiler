
int topLevelCall (){
    return 9;
}


int anotherFunction (){
    return 5 + topLevelCall () + 5 + topLevelCall ();
}

int main(){
    int a;
    a = anotherFunction();
    return a;
}
