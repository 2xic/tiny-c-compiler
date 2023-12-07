"""
https://dev.to/icyphox/python-for-reverse-engineering-1-elf-binaries-1fo4
"""
from elftools.elf.elffile import ELFFile, RelocationSection

with open('./bins/main.o', 'rb') as f:
    e = ELFFile(f)
    for section in e.iter_sections():
        #print(hex(section["sh_addr"]), section.name)
        #print(section.data())
        #print(section.data().hex())
        #print("")

        if isinstance(section, RelocationSection):
            symbol_table = e.get_section(section['sh_link'])
            for relocation in section.iter_relocations():
                symbol = symbol_table.get_symbol(relocation['r_info_sym'])
                addr = hex(relocation['r_offset'])
                print(f'{symbol.name} {addr}')
            #    exit(0)

"""

"""
