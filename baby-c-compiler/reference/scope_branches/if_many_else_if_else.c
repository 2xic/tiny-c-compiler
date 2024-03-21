
int callValue(int a){
    if (a == 2) {
        return 2;
    } else if (a == 6){
        return 22;
    } else if (a == 12){
        return 44;
    } else if (a == 18){
        return 64;
    } else {
        return 8;
    }
}

int main(){
    int a = callValue(2); 
    int b = callValue(6);
    int c = callValue(12);
    int d = callValue(18);
    int e = callValue(9);

    int results = a + b +c + d + e;
    
    return results;
}
