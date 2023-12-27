
int callValue(int a){
    if (a == 2) {
        return 2;
    } else if (a == 6){
        return 22;
    } else {
        return 8;
    }
}

int main(){
    int a = callValue(2); 
    int b = callValue(6);
    int c = callValue(9);

    int results = a + b +c;
    
    return results;
}
