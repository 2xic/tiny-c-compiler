int* sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    return current_program_offset;
}

struct memory_blocks {
    struct memory_blocks *next; // 8
};

struct memory_blocks *global_memory_blocks; // Tracks the start
struct memory_blocks *last_memory_blocks;   // Tracks the end

int* malloc(){
    int total = 16;
    int* pointer = sbrk(total);
    struct memory_blocks *test = pointer;    // This is the end of the previous segment
    test->next = 0;                          // We write the next variable

    global_memory_blocks =  test; // This reference should just be a pointer written into
    last_memory_blocks =    test;   // This assign messes up the code 

    return global_memory_blocks;
}


int main(){
    malloc();

    struct memory_blocks *current = global_memory_blocks;
    int a = 0;

    while(current != 0){
        current = current->next;
        a++;
    }
    return a; // Should return 1
}
