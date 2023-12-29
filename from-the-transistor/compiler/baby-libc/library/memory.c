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

// NOTE: This is the opposite from the C standard library
int memcpy(int from_address, int to_address, int size){
    // Copy from source destination to the target
    // TODO: Need a pointer access nodes implemented on the AST side
}

int* free(int *value){
    // TODO: We need to find the memory section inside the memory region
    // TODO: Wee need memcpy first http://www.danielvik.com/2010/02/fast-memcpy-in-c.html

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
    // test->free = size;
    
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

/**
 * DEBUG UTILS WHILE WORKING ON THIS
*/
int getSize(){
    int a = 0; 
    /*
    struct memory_blocks *current = last_memory_blocks;

    while(current != 0){
        a++;
        write(1, 1, "one round in the while loop\n");
        current = current->next;
    }
    */

    return a;
}
