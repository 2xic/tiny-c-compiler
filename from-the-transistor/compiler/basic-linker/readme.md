The compiler is starting to take shape, let's think some about the linker
- https://hzliu123.github.io/linux-kernel/Using%20GNU%20Compiler%20and%20Binutils%20by%20Example.pdf
- https://stackoverflow.com/a/30507725
  - Linkers work like the solc linker -> Use placeholder and fill them in later
- Okay, looking at the output they just write it to `External Symbols Segment` in the ELF binary
- https://gist.github.com/DhavalKapil/2243db1b732b211d0c16fd5d9140ab0b
- When linking this all get merged into one big file
- [Good paper from CMU](http://csapp.cs.cmu.edu/2e/ch7-preview.pdf)
- [Slides on Linker](https://accu.org/conf-docs/PDFs_2017/Peter_Smith_Slides.pdf)
- [Cornell](http://www.cs.cornell.edu/courses/cs3410/2013sp/lecture/14-linkers-w-g.pdf)


So in the assembly file they just mark it as a `@PLT` section
- https://reverseengineering.stackexchange.com/questions/1992/what-is-plt-got
- 

### Job of the linker
- Re-allocate the .data and .text sections
- Resolve unresolved symbols
- 
- 

## Elf
- https://nutcrackerssecurity.github.io/posts/elf-binary/

## Inspecting elf 
```
readelf -l ./elf_file
```

