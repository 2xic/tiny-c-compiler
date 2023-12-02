.text
        .global _start # Tell the loader we want to start at _start.

_start:
        movl    $2,%ebx # The argument to our system call.
        movl    $1,%eax # The system call number of sys_exit is 1.
        int     $0x80 # Send an interrupt
