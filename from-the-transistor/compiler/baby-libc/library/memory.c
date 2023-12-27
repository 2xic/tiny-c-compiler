/**
 * Memory operations in our own libc like library
*/

int* sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    if (return_value == -1){
        return -1;
    }
    return current_program_offset;
}

struct memory_blocks {
    int size; // 4
    int free; // 4
    struct memory_blocks *next; // 8
};

struct memory_blocks *global_memory_blocks;
struct memory_blocks *last_memory_blocks;


// WIP THIS section
int* free(int* memory){
    // TODO: We need to find the memory section inside the memory region
    return 0;
}

int* malloc(int size){

    int MEMORY_BLOCK_SIZE_STRUCT = 16; // TODO: implement sizeof(struct memory_blocks);
    // We need to allocate
    int total_size = MEMORY_BLOCK_SIZE_STRUCT + size;
    int value_ref = sbrk(total_size);
    struct memory_blocks *test = value_ref;
    // test = sbrk(total_size);
    
    test->size = size;
    test->free = size;
    
    if (global_memory_blocks == 0){
        global_memory_blocks = test;
        last_memory_blocks = test;
        return global_memory_blocks;
    } else {
        // Memory locations should be zero at this point
        // TODO: Fix this
//        last_memory_blocks->next = test;
        last_memory_blocks = test;
    }

    return last_memory_blocks;
}
