int* sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    return current_program_offset;
}

struct memory_blocks {
    // Switching the order here messes up the dereference logic.
    int size; // 4
    int free; // 4
    struct memory_blocks *next; // 8
};

struct memory_blocks *global_memory_blocks; // Tracks the start
struct memory_blocks *last_memory_blocks;

int* malloc(int size){
    int* pointer = sbrk(20);
    struct memory_blocks *test = pointer;    // This is the end of the previous segment
    
    test->size = size;
    test->free = size;
    test->next = 0;
    
    if (global_memory_blocks == 0){
        global_memory_blocks = test;
        last_memory_blocks = test; // THIS SHOULD COPY REFERENCE ... IS IT DOING THAT ?
        return global_memory_blocks;
    } else {
        // Memory locations should be zero at this point
        last_memory_blocks->next = test;
        last_memory_blocks = test;
    }

    return last_memory_blocks;
}

int getSize(){
    struct memory_blocks *current = global_memory_blocks;
    
    int a = 0;

    while(current != 0){
        a++;
        current = current->next;
    }

    return a;
}

int main(){
    int *a = malloc(4); // Set the global memory block
  //  *a = 9;
    int *b = malloc(4); // Set the global memory block
//    *b = 9;

    int c = getSize();

    return c;
}
