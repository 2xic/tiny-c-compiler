
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
    int results = callValue(2) + callValue(6) + callValue(9);
    
    return results;
}
