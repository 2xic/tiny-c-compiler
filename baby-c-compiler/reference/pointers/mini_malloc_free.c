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
    int MEMORY_BLOCK_SIZE_STRUCT = 24; // TODO: implement sizeof(struct memory_blocks); Currently we allocate one variable = 8
    // We need to allocate
    int total_size = MEMORY_BLOCK_SIZE_STRUCT + size;

    int value_ref = sbrk(total_size);
    struct memory_blocks *test = value_ref;
    
    test->size = size;
    test->free = size;
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

int* free(int *value){    
    struct memory_blocks *prev = global_memory_blocks;
    int a = 0;

    while(a == 0){
        struct memory_blocks *current = prev->next;
        struct memory_blocks *current_next = current->next;

        if (current_next == 0){
            a = 1;
        } else {
            prev = prev->next;
        }
    }

    prev->next = 0;

    return 0;
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

int sumFree(){
    struct memory_blocks *current = global_memory_blocks;
    
    int a = 0;

    while(current != 0){
        int value = current->size;
        a = a + value;
        current = current->next;
    }

    return a;
}

int main(){
    int *a = malloc(4); // Set the global memory block
    int *b = malloc(4); // Set the global memory block

    /**
      *  Before the call
      *                 size            free
        0x403000:       0x4     0x0     0x4     0x0
                        next pointer            size
        0x403010:       0x40301c        0x0     0x0     0x4
                        free            next pointer
        0x403020:       0x0     0x4     0x0     0x0
    */

//    free(a);

    /**
     *  After call
    *                  size             free
        0x403000:       0x4     0x0     0x4     0x0
                        next pointer    size
        0x403010:       0x40301c        0x0     0x0     0x0
                        free
        0x403020:       0x0     0x0     0x0     0x0

        Looks we are erasing the last pointer instead of the next last ... ? 

        Adding a debug point and verified this is the case ....
    */

   free(b);

    int c = getSize();

    return c;
}
