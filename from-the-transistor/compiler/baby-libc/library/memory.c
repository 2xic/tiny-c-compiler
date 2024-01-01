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
    int free; // 8 (should be 4)
    int size; // 8 (should be 4)
    struct memory_blocks *next; // 8
};

struct memory_blocks *global_memory_blocks;
struct memory_blocks *last_memory_blocks;

// WIP THIS section

// NOTE: This is the opposite argument order from the C standard library
int memcpy(int *from_address, int *to_address, int size) {
    // Copy from source destination to the target
    // TODO: Need a pointer access nodes implemented on the AST side
    
    for(int v = 0; v < size; v++){
        int value = *from_address;
        *to_address = value;

        from_address++;
        to_address++;
    }

    return 0;
}

int* free(int *value){
    // TODO: We need to find the memory section inside the memory region
    // TODO: Wee need memcpy first http://www.danielvik.com/2010/02/fast-memcpy-in-c.html
    
    struct memory_blocks *prev = global_memory_blocks;
    int run = 0;
    int count = 0;
    while(run == 0){
        int *adjustedValuePointer = value - 24; // Adjust to start of the block
        // This pointer == the free pointer
        if (prev == adjustedValuePointer){
            run = 1;
        }
        // If the next pointer is the current pointer then break
        struct memory_blocks *current = prev->next;
        if (current == 0){
            run = 2; // FAILED
        } else {
            count++;
            if (current == adjustedValuePointer){
                run = 1;
            } else {
                prev = prev->next;
            }
        }
    }

    int oldSize = prev->size;
    prev->free = 1;

    /**
     * We could be more fancy here and also merge in allocation etc. after a block is freed
    */

    return 0;
}

int *findFreeChunk(int size){
    // If we find a chunk that is free we can just use that instead ... 
    struct memory_blocks *current = global_memory_blocks;
    while(current != 0){
        int isFree = current->free;
        // We found a free chunk !
        if (isFree == 1){
            int value = current->size;
            if (value <= size){
                return current;
            }
        }
        current = current->next;
    }
    return 0;
}

int* malloc(int size){
    int MEMORY_BLOCK_SIZE_STRUCT = 24; // TODO: implement sizeof(struct memory_blocks); Currently we allocate one variable = 8

    int sizeCopy = size; // TODO: fix this call
    struct memory_blocks *reallocate = findFreeChunk(sizeCopy);

    if (reallocate != 0){
        reallocate->free = 0;
        int adjustedPointer = reallocate + 24;
        return adjustedPointer;
    }

    // We need to allocate
    int total_size = MEMORY_BLOCK_SIZE_STRUCT + size;

    int value_ref = sbrk(total_size);

    struct memory_blocks *test = value_ref;
    
    test->size = size;
    test->free = 0;
    test->next = 0;
    
    if (global_memory_blocks == 0){
        global_memory_blocks = test;
        last_memory_blocks = test; // THIS SHOULD COPY REFERENCE ... IS IT DOING THAT ?
    } else {
        // Memory locations should be zero at this point
        last_memory_blocks->next = test;
        last_memory_blocks = test;
    }

    // Move it forward so that we don't overwrite the metadata
    int adjustedPointer = last_memory_blocks + 24;


    return adjustedPointer;
}

/**
 * DEBUG UTILS WHILE WORKING ON THIS
*/
int getSize(){
    int a = 0; 

    struct memory_blocks *current = global_memory_blocks;

    while(current != 0){
        int isFree = current->free;
        if (isFree == 0){
            a = a + 1;
        }
        current = current->next;
    }

    return a;
}

/**
 * I noticed that we don't correctly create the struct in memory (only the pointers)
*/
int sumSize(){
    struct memory_blocks *current = global_memory_blocks;
    
    int a = 0;

    while(current != 0){
        int isFree = current->free;
        if (isFree == 0){
            int value = current->size;
            a = a + value;
        }
        current = current->next;
    }

    return a;
}

int sumFree(){
    struct memory_blocks *current = global_memory_blocks;
    
    int a = 0;

    while(current != 0){
        int isFree = current->free;
        if (isFree == 0){
            int value = current->free;
            a = a + value;
        }
        current = current->next;
    }

    return a;
}
