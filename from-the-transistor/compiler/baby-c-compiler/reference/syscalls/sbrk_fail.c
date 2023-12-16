// Reimplementing example of https://stackoverflow.com/a/31082353

int main() {
    int *b = brk(0); // This is the address
    // We allocate some heap memory ... I love the heap

    *b = 1;
    return 0;
}
