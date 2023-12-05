# Status
Currently we only support very basic stuff. No printf, no fancy stuff.

You can basically not do anything more fancy than what is shown below (yet)
```c
int anotherFunction (int a, int b){
    return a + b;
}

int main(){
    int a = anotherFunction(5, 9);
    
    return a;
}
```

## Resources
- https://www.wilfred.me.uk/blog/2014/08/27/baby-steps-to-a-c-compiler/

## Optimizations
- Remove unreadable code

## Asm
- https://www.cs.mcgill.ca/~cs573/fall2004/classnotes/Assem_Linux.pdf
- Using the stack
  - https://en.wikibooks.org/wiki/X86_Disassembly/The_Stack   

## Registers
- https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture
- https://www.quora.com/When-writing-a-compiler-how-do-you-manage-registers-for-arguments-and-temporary-values-Is-there-an-algorithm-that-takes-into-account-the-number-of-general-purpose-registers-available
- https://en.wikipedia.org/wiki/Register_allocation

## Some implementation that other people have implemented
Mostly to just get an idea of features that people commonly implement for this (most people don't fully implement c)

- https://github.com/Wilfred/babyc#current-feature-set

