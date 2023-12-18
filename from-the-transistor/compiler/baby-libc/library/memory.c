/**
 * Memory operations in our own libc like library
*/

int sbrk(int increment) {
    int current_program_offset = brk(0);
    int adjustment = current_program_offset + increment;
    int return_value = brk(adjustment);
    if (return_value == -1){
        return -1;
    }
    // TODO: Return the pointer.
    return 5;
}
