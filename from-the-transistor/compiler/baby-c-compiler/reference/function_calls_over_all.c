
int anotherFunction (){
    return 5+ 4;
}

int main(){
    int a;
    a = anotherFunction() + anotherFunction()+ anotherFunction() + 5;
    // This is reassigned .. need to zero it out
    a = anotherFunction() + anotherFunction()+ anotherFunction() + 5;
    
    return a;
}
