
int main(){
    int value = 42;
    
    int e;

    int *p = &value;

    int d;
    
    int c = *p; // 42

    int sum = c + value;

    return sum;
}
