int* sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    if (return_value == -1){
        return -1;
    }
    return current_program_offset;
}

int main(){
    int* a = sbrk(20);
    *a = 4;

    int p = *a;

    return p;
}
