
int *globalValue;

int main(){
    int value = 42;
    /**
     * 
     * Noise pointers
    */
    int *v = &value;
    
    int *p = &value;
    // This should reference the p
    globalValue = p;   
    *globalValue = 92;


    return globalValue;
}
