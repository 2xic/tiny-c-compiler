int* sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    return current_program_offset;
}

struct memory_blocks {
    // Switching the order here messes up the dereference logic.
    int size; // 4
    struct memory_blocks *next; // 8
};

struct memory_blocks *global_memory_blocks; // Tracks the start

int* malloc(){
    int* pointer = sbrk(20);
    struct memory_blocks *test = pointer;    // This is the end of the previous segment
    
    test->next = 0;
    test->size = 42;

    if (global_memory_blocks == 0){
        global_memory_blocks = test;
        return global_memory_blocks;
    } else {
        // Memory locations should be zero at this point
        // I think this pointer isn't moved correctly
        global_memory_blocks->next = 0;
    }

    return global_memory_blocks;
}


int main(){
    malloc(); // Set the global memory block
    malloc(); // Set the global memory block

    struct memory_blocks *current = global_memory_blocks;
    
    int value = current->size;
    int pointer = current->next;

    if (pointer == 0){
        if (value == 42){
            return 2;
        } else {
            return 1;
        }
    }

    return 0;
}
