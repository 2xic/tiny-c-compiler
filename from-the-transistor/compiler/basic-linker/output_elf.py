"""
So the world worst linker - 

I can read out the text section of the binaries and construct the ELF again

https://kevinboone.me/elfdemo.html?i=1
"""
from elf_parser import FileHeader, ProgramHeader

file_header = FileHeader.create()
program_header = ProgramHeader.create()
